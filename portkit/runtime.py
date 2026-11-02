"""Small, game-neutral runtime contracts for bounded 3DS prototypes.

These types are a schema and validation layer, not a game importer or an
interpreter for a commercial engine.  Applications supply their own adapter
and translate only content they are entitled to use.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Mapping, Protocol, Sequence


EVENT_SCHEMA_VERSION = 1
SUPPORTED_OPCODES = frozenset({"nop", "set_flag", "wait_frames", "show_notice", "transfer"})


@dataclass(frozen=True)
class EventInstruction:
    opcode: str
    arguments: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EventProgram:
    """A bounded, declarative event program; it deliberately has no script opcode."""
    event_id: str
    instructions: tuple[EventInstruction, ...]
    schema_version: int = EVENT_SCHEMA_VERSION

    def validate(self, max_instructions: int = 256) -> None:
        if self.schema_version != EVENT_SCHEMA_VERSION:
            raise ValueError("unsupported event schema version")
        if not self.event_id or len(self.event_id) > 64:
            raise ValueError("event_id must be 1-64 characters")
        if len(self.instructions) > max_instructions:
            raise ValueError("event program exceeds instruction budget")
        for instruction in self.instructions:
            if instruction.opcode not in SUPPORTED_OPCODES:
                raise ValueError(f"unsupported event opcode: {instruction.opcode}")

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)


class EngineAdapter(Protocol):
    """Minimal boundary an independently-written engine adapter must implement."""
    def load_map(self, map_id: str) -> "MapLifecycle": ...
    def poll_input(self) -> "InputState": ...
    def save_snapshot(self) -> "SaveSnapshot": ...
    def restore_snapshot(self, snapshot: "SaveSnapshot") -> None: ...


@dataclass(frozen=True)
class MapLifecycle:
    map_id: str
    width_tiles: int
    height_tiles: int
    collision_cells: tuple[int, ...]
    events: tuple[EventProgram, ...] = ()

    def validate(self, max_tiles: int = 8192, max_events: int = 512) -> None:
        if not self.map_id or self.width_tiles < 1 or self.height_tiles < 1:
            raise ValueError("map id and dimensions must be positive")
        if self.width_tiles * self.height_tiles > max_tiles:
            raise ValueError("map exceeds tile budget")
        if len(self.collision_cells) != self.width_tiles * self.height_tiles:
            raise ValueError("collision cells must match map dimensions")
        if any(cell not in (0, 1) for cell in self.collision_cells):
            raise ValueError("collision cells must be 0 (walkable) or 1 (blocked)")
        if len(self.events) > max_events:
            raise ValueError("map exceeds event budget")
        for event in self.events:
            event.validate()


@dataclass(frozen=True)
class InputState:
    pressed: frozenset[str] = frozenset()
    held: frozenset[str] = frozenset()
    touch: tuple[int, int] | None = None


@dataclass(frozen=True)
class SaveSnapshot:
    """Logical state only: adapters must never serialize runtime pointers."""
    schema_version: int
    map_id: str
    player_tile: tuple[int, int]
    flags: Mapping[str, bool]

    def validate(self, max_flags: int = 256) -> None:
        if self.schema_version != 1 or not self.map_id or len(self.flags) > max_flags:
            raise ValueError("invalid save snapshot")
        if min(self.player_tile) < 0 or not all(isinstance(v, bool) for v in self.flags.values()):
            raise ValueError("invalid snapshot values")


@dataclass(frozen=True)
class ResourceBudget:
    max_texture_bytes: int = 4 * 1024 * 1024
    max_map_tiles: int = 8192
    max_event_instructions: int = 256

    def validate_texture_bytes(self, value: int) -> None:
        if value > self.max_texture_bytes:
            raise ValueError(f"texture budget exceeded: {value} > {self.max_texture_bytes}")


def renderer_diagnostics(work_ms: float, total_ms: float, resident_bytes: int,
                         budget: ResourceBudget = ResourceBudget()) -> dict:
    """Return explicitly scoped diagnostics; only total time is a frame result."""
    if work_ms < 0 or total_ms < work_ms or resident_bytes < 0:
        raise ValueError("invalid renderer measurement")
    return {"work_ms": work_ms, "total_ms": total_ms, "resident_bytes": resident_bytes,
            "texture_budget_bytes": budget.max_texture_bytes,
            "resident_within_texture_budget": resident_bytes <= budget.max_texture_bytes,
            "note": "Host/emulator diagnostics are not original-3DS hardware measurements."}
