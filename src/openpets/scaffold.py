from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

from openpets.contract import (
    ANIMATION_ROWS,
    ATLAS_HEIGHT,
    ATLAS_WIDTH,
    CELL_HEIGHT,
    CELL_WIDTH,
    is_used_cell,
)

PET_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ScaffoldError(RuntimeError):
    pass


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def scaffold_pet(
    repo_root: Path,
    pet_id: str,
    display_name: str,
    description: str,
    *,
    author: str,
    asset_license: str,
) -> Path:
    if not PET_ID.fullmatch(pet_id):
        raise ScaffoldError("Pet id must be lowercase kebab-case.")

    resolved_repo_root = repo_root.resolve()
    pets_root = repo_root / "pets"
    if pets_root.is_symlink():
        raise ScaffoldError(f"Refusing symlinked pets directory: {pets_root}")
    resolved_pets_root = pets_root.resolve()
    if not _is_within(resolved_pets_root, resolved_repo_root):
        raise ScaffoldError(f"Pets directory must stay inside the repository: {resolved_pets_root}")

    destination = pets_root / pet_id
    resolved_destination = destination.resolve()
    if not _is_within(resolved_destination, resolved_repo_root):
        raise ScaffoldError(
            f"Pet destination must stay inside the repository: {resolved_destination}"
        )
    if destination.is_symlink():
        raise ScaffoldError(f"Refusing symlinked pet destination: {destination}")
    if destination.exists():
        raise ScaffoldError(f"Pet already exists: {destination}")
    source_dir = destination / "source"
    source_dir.mkdir(parents=True)

    manifest = {
        "id": pet_id,
        "displayName": display_name,
        "description": description,
        "spriteVersionNumber": 2,
        "spritesheetPath": "spritesheet.webp",
    }
    metadata = {
        "$schema": "../../schemas/pet-metadata.schema.json",
        "schemaVersion": 1,
        "version": "0.1.0",
        "authors": [{"name": author}],
        "assetLicense": asset_license,
        "spritesheetSha256": "replace-with-final-lowercase-sha256",
        "tags": [],
        "provenance": {
            "aiAssisted": False,
            "thirdPartyCharacter": False,
            "redistributionConfirmed": False,
        },
        "testedWith": {"codexDesktop": "not-yet-tested"},
    }
    (destination / "pet.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "pet.meta.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "README.md").write_text(
        f"# {display_name}\n\n{description}\n\nAdd a preview after the spritesheet is ready.\n",
        encoding="utf-8",
    )
    (destination / "LICENSE-ASSETS.md").write_text(
        f"# Asset license\n\nDeclared license: `{asset_license}`.\n\n"
        "Replace this note with complete terms and attribution before opening a pull request.\n",
        encoding="utf-8",
    )
    (source_dir / "README.md").write_text(
        "# Source files\n\n"
        "Keep editable source, prompts, palette notes, and export instructions here.\n",
        encoding="utf-8",
    )

    guide = Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(guide)
    for row in ANIMATION_ROWS:
        for column in range(8):
            x0 = column * CELL_WIDTH
            y0 = row.index * CELL_HEIGHT
            fill = (229, 245, 235, 255) if is_used_cell(row, column) else (238, 238, 238, 255)
            draw.rectangle((x0, y0, x0 + CELL_WIDTH - 1, y0 + CELL_HEIGHT - 1), fill=fill)
            draw.rectangle(
                (x0, y0, x0 + CELL_WIDTH - 1, y0 + CELL_HEIGHT - 1), outline=(80, 86, 96, 255)
            )
            draw.text((x0 + 8, y0 + 8), f"{row.index}:{column} {row.state}", fill=(30, 34, 40, 255))
    guide.save(source_dir / "atlas-guide.png")
    return destination
