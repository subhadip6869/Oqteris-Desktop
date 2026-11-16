"""Command-pattern Undo and Redo manager for PDF document operations."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class Command(ABC):
    """Abstract base command for undoable actions."""

    @abstractmethod
    def execute(self) -> bool:
        """Perform or re-apply the action."""
        pass

    @abstractmethod
    def undo(self) -> bool:
        """Reverse the action."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable command description."""
        pass


class UndoRedoStack:
    """Maintains history of undoable commands per document."""

    def __init__(self, max_history: int = 50) -> None:
        self.max_history = max_history
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    @property
    def undo_command_name(self) -> str:
        return self._undo_stack[-1].name if self._undo_stack else ""

    @property
    def redo_command_name(self) -> str:
        return self._redo_stack[-1].name if self._redo_stack else ""

    def push_and_execute(self, command: Command) -> bool:
        """Execute command and push to undo stack if successful."""
        success = command.execute()
        if success:
            self._undo_stack.append(command)
            self._redo_stack.clear()
            if len(self._undo_stack) > self.max_history:
                self._undo_stack.pop(0)
        return success

    def undo(self) -> bool:
        """Undo top command from undo stack."""
        if not self.can_undo:
            return False

        command = self._undo_stack.pop()
        success = command.undo()
        if success:
            self._redo_stack.append(command)
        else:
            logger.error("Undo failed for command: %s", command.name)
        return success

    def redo(self) -> bool:
        """Redo top command from redo stack."""
        if not self.can_redo:
            return False

        command = self._redo_stack.pop()
        success = command.execute()
        if success:
            self._undo_stack.append(command)
        else:
            logger.error("Redo failed for command: %s", command.name)
        return success

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()
