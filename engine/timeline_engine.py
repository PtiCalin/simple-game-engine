from dataclasses import dataclass
from typing import List, Optional, Dict

from .game_state import GameState


@dataclass
class TimelineEvent:
    """Single scheduled event."""

    trigger: str
    time: int  # milliseconds
    action: str
    flag: Optional[str] = None
    scene: Optional[str] = None
    scheduled_at: int = 0


class TimelineEngine:
    """Manage time-based events for scenes or globally."""

    def __init__(self, state: GameState):
        self.state = state
        self.events: List[TimelineEvent] = []

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------
    def add_events(self, entries: List[Dict], current_ticks: int, scene: Optional[str] = None) -> None:
        """Load events from a list of dictionaries."""
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            trigger = entry.get("trigger")
            time_val = entry.get("time", 0)
            action = entry.get("action")
            flag = entry.get("flag")
            if trigger != "delay" or action is None:
                continue
            try:
                delay_ms = int(float(time_val) * 1000)
            except (TypeError, ValueError):
                delay_ms = 0
            self.events.append(
                TimelineEvent(
                    trigger="delay",
                    time=delay_ms,
                    action=action,
                    flag=flag,
                    scene=scene,
                    scheduled_at=current_ticks,
                )
            )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, current_ticks: int, current_scene: Optional[str] = None) -> None:
        """Trigger events whose timers have elapsed."""
        to_remove: List[TimelineEvent] = []
        for event in self.events:
            if event.scene and event.scene != current_scene:
                continue
            if event.trigger == "delay" and current_ticks - event.scheduled_at >= event.time:
                self._execute(event)
                to_remove.append(event)
        for ev in to_remove:
            self.events.remove(ev)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------
    def _execute(self, event: TimelineEvent) -> None:
        if event.action == "set_flag" and event.flag:
            self.state.set_flag(event.flag, True)
            self.state.save()
