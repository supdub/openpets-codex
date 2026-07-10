from __future__ import annotations

import json

from PIL import Image

from openpets.contract import ATLAS_HEIGHT, ATLAS_WIDTH, CELL_HEIGHT, CELL_WIDTH
from openpets.validate import validate_pet
from tests.helpers import make_pet


def test_valid_pet_passes(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    result = validate_pet(pet_dir, strict=True)
    assert result.ok, result.to_dict()


def test_manifest_id_must_match_folder(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    path = pet_dir / "pet.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["id"] = "someone-else"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    result = validate_pet(pet_dir)
    assert "manifest.id-mismatch" in {issue.code for issue in result.errors}


def test_unused_cell_must_be_transparent(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    sprite = pet_dir / "spritesheet.webp"
    with Image.open(sprite) as source:
        image = source.convert("RGBA")
    x = 7 * CELL_WIDTH + 30
    y = 0 * CELL_HEIGHT + 30
    image.putpixel((x, y), (255, 0, 0, 255))
    image.save(sprite, format="WEBP", lossless=True)
    result = validate_pet(pet_dir)
    assert "atlas.nonempty-unused-cell" in {issue.code for issue in result.errors}


def test_neutral_look_cell_must_be_present(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    sprite = pet_dir / "spritesheet.webp"
    with Image.open(sprite) as source:
        image = source.convert("RGBA")
    image.paste(
        (0, 0, 0, 0),
        (6 * CELL_WIDTH, 0, 7 * CELL_WIDTH, CELL_HEIGHT),
    )
    image.save(sprite, format="WEBP", lossless=True)
    result = validate_pet(pet_dir)
    assert "atlas.empty-used-cell" in {issue.code for issue in result.errors}


def test_wrong_dimensions_fail(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT - 1)).save(
        pet_dir / "spritesheet.webp", format="WEBP", lossless=True
    )
    result = validate_pet(pet_dir)
    assert "atlas.dimensions" in {issue.code for issue in result.errors}


def test_metadata_requires_schema_fields_and_redistribution_confirmation(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    path = pet_dir / "pet.meta.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata.pop("tags")
    metadata.pop("testedWith")
    metadata["unexpected"] = True
    metadata["provenance"]["redistributionConfirmed"] = False
    path.write_text(json.dumps(metadata), encoding="utf-8")

    result = validate_pet(pet_dir, strict=True)
    codes = {issue.code for issue in result.errors}
    assert "metadata.missing-fields" in codes
    assert "metadata.unknown-fields" in codes
    assert "metadata.redistribution-not-confirmed" in codes


def test_strict_validation_requires_committed_previews(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    (pet_dir / "preview" / "00-idle.gif").unlink()
    result = validate_pet(pet_dir, strict=True)
    assert "strict.preview.missing" in {issue.code for issue in result.errors}


def test_metadata_rejects_boolean_schema_version_and_non_string_author(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    path = pet_dir / "pet.meta.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["schemaVersion"] = True
    metadata["authors"] = [{"name": True}]
    path.write_text(json.dumps(metadata), encoding="utf-8")

    result = validate_pet(pet_dir, strict=True)
    codes = {issue.code for issue in result.errors}
    assert "metadata.schema-version" in codes
    assert "metadata.authors" in codes
