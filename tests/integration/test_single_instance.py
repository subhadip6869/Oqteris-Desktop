"""Integration tests for single instance IPC handling and startup arguments."""

import os
import pytest
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtCore import QCoreApplication

from oqteris.application.single_instance import SingleInstanceCoordinator


@pytest.fixture(scope="session")
def qcore_app():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


def test_single_instance_startup(qcore_app, temp_dir: Path):
    coordinator = SingleInstanceCoordinator(app_id="org.originsd.oqteris.test")
    # First launch should be primary
    is_primary = coordinator.handle_startup([])
    assert is_primary is True

    coordinator.close()
