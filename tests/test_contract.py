from openpets.contract import (
    ANIMATION_ROWS,
    ATLAS_HEIGHT,
    ATLAS_WIDTH,
    CELL_HEIGHT,
    CELL_WIDTH,
)


def test_v2_geometry_is_internally_consistent() -> None:
    assert (ATLAS_WIDTH, ATLAS_HEIGHT) == (1536, 2288)
    assert ATLAS_WIDTH == CELL_WIDTH * 8
    assert ATLAS_HEIGHT == CELL_HEIGHT * 11
    assert [row.frames for row in ANIMATION_ROWS] == [6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8]
    assert ANIMATION_ROWS[9].directions[0] == "000"
    assert ANIMATION_ROWS[10].directions[-1] == "337.5"
