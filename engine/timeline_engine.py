from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict

from .game_state import GameState

if False:  # pragma: no cover - for type checkers
    from .scene_manager import SceneManager


@dataclass
class TimelineEvent:
    """Represents a single scheduled event."""

    id: str
    trigger: str
    time: float
    action: str
    params: Dict[str, object] = field(default_factory=dict)
    condition: Optional[str] = None
    scene: Optional[str] = None
    scheduled_at: float = 0.0
    triggered: bool = False

    def is_ready(self, current_time: float, state: GameState) -> bool:
        """Return ``True`` if the event should fire."""
        if self.triggered:
            return False
        if self.trigger == "delay":
            return current_time - self.scheduled_at >= self.time
        if self.trigger == "condition":
            if not state.check_condition(self.condition):
                return False
            return current_time - self.scheduled_at >= self.time
        if self.trigger == "scene":
            return True
        return False

    def execute(self, state: GameState, manager: "SceneManager | None") -> None:
        """Carry out the event action."""
        if self.action == "set_flag":
            flag = self.params.get("flag")
            if isinstance(flag, str):
                state.set_flag(flag, True)
                state.save()
        elif self.action == "toggle_flag":
            flag = self.params.get("flag")
            if isinstance(flag, str):
                state.toggle_flag(flag)
                state.save()
        elif self.action == "show_dialogue" and manager:
            text = self.params.get("text")
            if isinstance(text, str) and manager.dialogue_engine:
                manager.dialogue_engine.start(text)
        elif self.action == "goto_scene" and manager:
            target = self.params.get("scene")
            if isinstance(target, str):
                manager.open_scene(target)
        # Additional actions can be plugged in here


class TimelineEngine:
    """Manage time-based events and optional looping timelines."""

    def __init__(self, state: GameState, scene_manager: "SceneManager | None" = None) -> None:
        self.events: List[TimelineEvent] = []
        self.elapsed_time: float = 0.0
        self.loop_enabled: bool = False
        self.loop_duration: float = 0.0
        self.game_state = state
        self.scene_manager = scene_manager
        self._last_tick: int = 0

    # ------------------------------------------------------------------
    # Scheduling helpers
    # ------------------------------------------------------------------
    def load_events(self, event_data: List[Dict[str, object]]) -> None:
        """Load events from a raw data list."""
        for entry in event_data:
            if not isinstance(entry, dict):
                continue
            trigger = entry.get("trigger", "delay")
            action = entry.get("action", "")
            params = entry.get("params", {}) or {}
            time_val = entry.get("time", entry.get("delay", 0))
            try:
                delay = float(time_val)
            except (TypeError, ValueError):
                delay = 0.0
            event = TimelineEvent(
                id=str(entry.get("id", "")),
                trigger=str(trigger),
                time=delay,
                action=str(action),
                params=params,
                condition=entry.get("condition"),
            )
            self.add_event(event)

    def add_event(self, event: TimelineEvent, scene: Optional[str] = None) -> None:
        """Add a :class:`TimelineEvent` instance."""
        event.scene = scene
        event.scheduled_at = self.elapsed_time
        self.events.append(event)

    # ------------------------------------------------------------------
    # Compatibility loader
    # ------------------------------------------------------------------
    def add_events(self, entries: List[Dict[str, object]], current_ticks: int, scene: Optional[str] = None) -> None:
        """Backwards compatible loader using ticks."""
        self._sync_ticks(current_ticks)
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            trigger = entry.get("trigger", "delay")
            action = entry.get("action", "")
            time_val = entry.get("time", entry.get("delay", 0))
            params: Dict[str, object] = {}
            if entry.get("flag"):
                params["flag"] = entry.get("flag")
            if entry.get("params"):
                params.update(entry.get("params"))
            try:
                delay = float(time_val)
            except (TypeError, ValueError):
                delay = 0.0
            ev = TimelineEvent(
                id=str(entry.get("id", "")),
                trigger=str(trigger),
                time=delay,
                action=str(action),
                params=params,
                condition=entry.get("condition"),
            )
            self.add_event(ev, scene)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, current_ticks: int, current_scene: Optional[str] = None) -> None:
        """Advance timers and fire ready events."""
        self._sync_ticks(current_ticks)
        to_remove: List[TimelineEvent] = []
        for event in self.events:
            if event.scene and current_scene and event.scene != current_scene:
                continue
            if event.is_ready(self.elapsed_time, self.game_state):
                self.trigger_event(event)
                if self.loop_enabled:
                    event.triggered = True
                    event.scheduled_at = self.elapsed_time
                else:
                    to_remove.append(event)
        for ev in to_remove:
            self.events.remove(ev)
        if self.loop_enabled and self.loop_duration > 0.0:
            if self.elapsed_time >= self.loop_duration:
                self.reset_loop()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _sync_ticks(self, current_ticks: int) -> None:
        if self._last_tick == 0:
            delta = current_ticks
            self._last_tick = current_ticks
            self.elapsed_time += delta / 1000.0
            return
        delta = current_ticks - self._last_tick
        if delta < 0:
            delta = 0
        self.elapsed_time += delta / 1000.0
        self._last_tick = current_ticks

    # ------------------------------------------------------------------
    # Execution and loop handling
    # ------------------------------------------------------------------
    def trigger_event(self, event: TimelineEvent) -> None:
        event.execute(self.game_state, self.scene_manager)

    def reset_loop(self) -> None:
        self.elapsed_time = 0.0
        self._last_tick = 0
        for ev in self.events:
            ev.triggered = False
            ev.scheduled_at = 0.0
