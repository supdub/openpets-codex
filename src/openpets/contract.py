from __future__ import annotations

from dataclasses import dataclass

SPRITE_VERSION = 2
CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
ROWS_COUNT = 11
ATLAS_WIDTH = CELL_WIDTH * COLUMNS
ATLAS_HEIGHT = CELL_HEIGHT * ROWS_COUNT
MAX_SPRITESHEET_BYTES = 20 * 1024 * 1024
NEUTRAL_LOOK_ROW = 0
NEUTRAL_LOOK_COLUMN = 6


@dataclass(frozen=True)
class AnimationRow:
    index: int
    state: str
    frames: int
    durations_ms: tuple[int, ...] | None = None
    directions: tuple[str, ...] | None = None


ANIMATION_ROWS = (
    # Codex multiplies the authored idle cadence by six at runtime.
    AnimationRow(0, "idle", 6, (1680, 660, 660, 840, 840, 1920)),
    AnimationRow(1, "running-right", 8, (120, 120, 120, 120, 120, 120, 120, 220)),
    AnimationRow(2, "running-left", 8, (120, 120, 120, 120, 120, 120, 120, 220)),
    AnimationRow(3, "waving", 4, (140, 140, 140, 280)),
    AnimationRow(4, "jumping", 5, (140, 140, 140, 140, 280)),
    AnimationRow(5, "failed", 8, (140, 140, 140, 140, 140, 140, 140, 240)),
    AnimationRow(6, "waiting", 6, (150, 150, 150, 150, 150, 260)),
    AnimationRow(7, "running", 6, (120, 120, 120, 120, 120, 220)),
    AnimationRow(8, "review", 6, (150, 150, 150, 150, 150, 280)),
    AnimationRow(
        9,
        "look-directions-a",
        8,
        directions=("000", "022.5", "045", "067.5", "090", "112.5", "135", "157.5"),
    ),
    AnimationRow(
        10,
        "look-directions-b",
        8,
        directions=("180", "202.5", "225", "247.5", "270", "292.5", "315", "337.5"),
    ),
)

ROW_BY_STATE = {row.state: row for row in ANIMATION_ROWS}


def is_used_cell(row: AnimationRow, column: int) -> bool:
    """Return whether Codex reads this atlas cell.

    Idle columns 0-5 are animated. Column 6 is a separate neutral look
    frame used while directional tracking is inactive.
    """

    return column < row.frames or (row.index == NEUTRAL_LOOK_ROW and column == NEUTRAL_LOOK_COLUMN)
