"""Non-destructive history and state snapshot manager."""

from __future__ import annotations
import time
from typing import List, Optional, Dict, Any
from PIL import Image

from autochrome.types import ActionRecord


class HistorySnapshot:
    """Represents a full state snapshot of the canvas."""

    def __init__(self, action: ActionRecord, image: Image.Image, metadata: Optional[Dict[str, Any]] = None):
        self.action = action
        self.image = image.copy()
        self.metadata = metadata or {}


class HistoryManager:
    """Manages undo/redo stacks and chronological action history."""

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.undo_stack: List[HistorySnapshot] = []
        self.redo_stack: List[HistorySnapshot] = []
        self.actions: List[ActionRecord] = []

    def push_state(self, tool_name: str, description: str, image: Image.Image, params: Dict[str, Any]):
        action = ActionRecord(
            id=f"act_{len(self.actions) + 1}",
            tool_name=tool_name,
            description=description,
            parameters=params,
            timestamp=time.time(),
        )
        snapshot = HistorySnapshot(action, image, params)
        self.undo_stack.append(snapshot)
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.actions.append(action)

    def undo(self) -> Optional[HistorySnapshot]:
        if len(self.undo_stack) <= 1:
            return None
        current = self.undo_stack.pop()
        self.redo_stack.append(current)
        return self.undo_stack[-1]

    def redo(self) -> Optional[HistorySnapshot]:
        if not self.redo_stack:
            return None
        target = self.redo_stack.pop()
        self.undo_stack.append(target)
        return target

    def get_current_snapshot(self) -> Optional[HistorySnapshot]:
        return self.undo_stack[-1] if self.undo_stack else None

    def get_action_list(self) -> List[Dict[str, Any]]:
        return [a.model_dump() for a in self.actions]
