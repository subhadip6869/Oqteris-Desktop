"""Ribbon state, active tool tracking, and undo/redo dispatching controller."""

from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

from oqteris.pdf.editing.undo_redo import UndoRedoStack

logger = logging.getLogger(__name__)


class RibbonController(QObject):
    """Manages active ribbon tab, selected pointer/markup tool, and undo/redo stacks."""

    currentTabChanged = Signal(str)
    activeToolChanged = Signal(str)
    undoRedoStateChanged = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._current_tab = "Home"
        self._active_tool = "select"  # "select", "hand", "highlight", "underline", "strikeout", "note", "ink", "shape", "stamp", "text", "image"
        self._undo_stack = UndoRedoStack()

    @Property(str, notify=currentTabChanged)
    def currentTab(self) -> str:
        return self._current_tab

    @currentTab.setter
    def currentTab(self, tab: str) -> None:
        if self._current_tab != tab:
            self._current_tab = tab
            self.currentTabChanged.emit(self._current_tab)

    @Property(str, notify=activeToolChanged)
    def activeTool(self) -> str:
        return self._active_tool

    @activeTool.setter
    def activeTool(self, tool: str) -> None:
        if self._active_tool != tool:
            self._active_tool = tool
            self.activeToolChanged.emit(self._active_tool)

    @Property(bool, notify=undoRedoStateChanged)
    def canUndo(self) -> bool:
        return self._undo_stack.can_undo

    @Property(bool, notify=undoRedoStateChanged)
    def canRedo(self) -> bool:
        return self._undo_stack.can_redo

    @Slot(str)
    def selectTab(self, tab_name: str) -> None:
        self.currentTab = tab_name

    @Slot(str)
    def selectTool(self, tool_name: str) -> None:
        self.activeTool = tool_name

    @Slot()
    def undo(self) -> None:
        if self._undo_stack.can_undo:
            self._undo_stack.undo()
            self.undoRedoStateChanged.emit()

    @Slot()
    def redo(self) -> None:
        if self._undo_stack.can_redo:
            self._undo_stack.redo()
            self.undoRedoStateChanged.emit()

    @property
    def undo_stack(self) -> UndoRedoStack:
        return self._undo_stack
