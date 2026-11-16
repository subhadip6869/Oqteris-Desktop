"""Single-instance application coordination and local IPC messaging using QLocalServer/QLocalSocket."""

from __future__ import annotations

import getpass
import json
import logging
import sys
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from oqteris.core.constants import APP_IDENTIFIER

logger = logging.getLogger(__name__)


class SingleInstanceCoordinator(QObject):
    """Coordinates single-instance enforcement and forwards command-line file arguments to running instance."""

    files_received = Signal(list)  # Emits list of str (file paths)

    def __init__(self, app_id: str = APP_IDENTIFIER, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        username = getpass.getuser()
        self.server_name = f"{app_id}_{username}_ipc"
        self._server: Optional[QLocalServer] = None

    def handle_startup(self, args: list[str]) -> bool:
        """Attempt to pass file arguments to an already-running primary instance.

        Returns True if this process is the PRIMARY instance and should continue running.
        Returns False if arguments were forwarded to an existing instance and this process should exit.
        """
        pdf_args = [
            str(Path(a).resolve())
            for a in args
            if Path(a).is_file() and a.lower().endswith(".pdf")
        ]

        # Try connecting to existing primary instance
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)

        if socket.waitForConnected(800):
            logger.info("Existing application instance found. Forwarding file arguments: %s", pdf_args)
            payload = json.dumps(pdf_args).encode("utf-8")
            socket.write(payload)
            socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
            return False  # Handled by primary, exit secondary

        # No running instance: initialize local server to listen for future secondary launches
        QLocalServer.removeServer(self.server_name)
        self._server = QLocalServer(self)
        self._server.newConnection.connect(self._on_new_connection)

        if not self._server.listen(self.server_name):
            logger.warning("Could not start single-instance IPC server: %s", self._server.errorString())

        return True  # This is the primary instance

    def _on_new_connection(self) -> None:
        """Invoked when a secondary instance connects to pass new file paths."""
        if not self._server:
            return

        client_socket = self._server.nextPendingConnection()
        if not client_socket:
            return

        if client_socket.waitForReadyRead(1000):
            data = client_socket.readAll().data().decode("utf-8")
            try:
                paths = json.loads(data)
                if isinstance(paths, list) and paths:
                    logger.info("Received new file opening request via IPC: %s", paths)
                    self.files_received.emit(paths)
            except Exception as e:
                logger.error("Failed to parse IPC payload: %s", e)

        client_socket.disconnectFromServer()
        client_socket.deleteLater()

    def close(self) -> None:
        if self._server:
            self._server.close()
            QLocalServer.removeServer(self.server_name)
            self._server = None
