from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from openpets.contract import (
    ANIMATION_ROWS,
    ATLAS_HEIGHT,
    ATLAS_WIDTH,
    CELL_HEIGHT,
    CELL_WIDTH,
    COLUMNS,
    is_used_cell,
)
from openpets.preview import render_previews


def make_pet(root: Path, pet_id: str = "test-pet") -> Path:
    pet_dir = root / "pets" / pet_id
    pet_dir.mkdir(parents=True)
    manifest = {
        "id": pet_id,
        "displayName": "Test Pet",
        "description": "A test fixture.",
        "spriteVersionNumber": 2,
        "spritesheetPath": "spritesheet.webp",
    }
    metadata = {
        "schemaVersion": 1,
        "version": "1.0.0",
        "authors": [{"name": "Tests"}],
        "assetLicense": "CC0-1.0",
        "tags": ["test"],
        "provenance": {
            "aiAssisted": False,
            "thirdPartyCharacter": False,
            "redistributionConfirmed": True,
        },
        "testedWith": {"codexDesktop": "test"},
    }
    (pet_dir / "pet.json").write_text(json.dumps(manifest), encoding="utf-8")
    (pet_dir / "README.md").write_text("# Test Pet\n", encoding="utf-8")
    (pet_dir / "LICENSE-ASSETS.md").write_text("CC0-1.0\n", encoding="utf-8")
    image = Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for row in ANIMATION_ROWS:
        for column in range(COLUMNS):
            if not is_used_cell(row, column):
                continue
            x = column * CELL_WIDTH + 24
            y = row.index * CELL_HEIGHT + 24
            draw.rectangle((x, y, x + 40, y + 64), fill=(220, 80, 160, 255))
    image.save(pet_dir / "spritesheet.webp", format="WEBP", lossless=True, method=6)
    metadata["spritesheetSha256"] = hashlib.sha256(
        (pet_dir / "spritesheet.webp").read_bytes()
    ).hexdigest()
    (pet_dir / "pet.meta.json").write_text(json.dumps(metadata), encoding="utf-8")
    render_previews(pet_dir)
    return pet_dir
