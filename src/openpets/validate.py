from __future__ import annotations

import hashlib
import re
import warnings
from pathlib import Path
from typing import Any

from PIL import Image

from openpets.catalog import CatalogError, load_json
from openpets.contract import (
    ANIMATION_ROWS,
    ATLAS_HEIGHT,
    ATLAS_WIDTH,
    CELL_HEIGHT,
    CELL_WIDTH,
    COLUMNS,
    MAX_SPRITESHEET_BYTES,
    SPRITE_VERSION,
    is_used_cell,
)
from openpets.models import ValidationResult

PET_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
REQUIRED_MANIFEST_FIELDS = {
    "id": str,
    "displayName": str,
    "description": str,
    "spriteVersionNumber": int,
    "spritesheetPath": str,
}
ALLOWED_MANIFEST_FIELDS = set(REQUIRED_MANIFEST_FIELDS)
REQUIRED_METADATA_FIELDS = {
    "schemaVersion",
    "version",
    "authors",
    "assetLicense",
    "spritesheetSha256",
    "tags",
    "provenance",
    "testedWith",
}
ALLOWED_METADATA_FIELDS = REQUIRED_METADATA_FIELDS | {"$schema"}


def _manifest_checks(result: ValidationResult, manifest: dict[str, Any], path: Path) -> Path | None:
    for key, expected in REQUIRED_MANIFEST_FIELDS.items():
        if key not in manifest:
            result.add("error", "manifest.missing-field", f"Missing required field {key!r}.", path)
        elif (expected is int and type(manifest[key]) is not int) or (
            expected is not int and not isinstance(manifest[key], expected)
        ):
            result.add(
                "error",
                "manifest.wrong-type",
                f"Field {key!r} must be {expected.__name__}.",
                path,
            )

    unknown = sorted(set(manifest) - ALLOWED_MANIFEST_FIELDS)
    if unknown:
        result.add(
            "warning",
            "manifest.unknown-fields",
            "Runtime pet.json should contain only the five app fields; "
            f"found: {', '.join(unknown)}.",
            path,
        )

    pet_id = manifest.get("id")
    if isinstance(pet_id, str):
        if not PET_ID.fullmatch(pet_id):
            result.add(
                "error", "manifest.invalid-id", "id must be a lowercase kebab-case slug.", path
            )
        if pet_id != result.pet_dir.name:
            result.add(
                "error",
                "manifest.id-mismatch",
                f"Manifest id {pet_id!r} must match folder {result.pet_dir.name!r}.",
                path,
            )

    if manifest.get("spriteVersionNumber") != SPRITE_VERSION:
        result.add(
            "error",
            "manifest.sprite-version",
            f"spriteVersionNumber must be {SPRITE_VERSION} for the v2 atlas.",
            path,
        )

    for key in ("displayName", "description"):
        value = manifest.get(key)
        if isinstance(value, str) and not value.strip():
            result.add("error", "manifest.empty-field", f"{key} cannot be empty.", path)
    display_name = manifest.get("displayName")
    if isinstance(display_name, str) and len(display_name) > 80:
        result.add(
            "error", "manifest.display-name-length", "displayName exceeds 80 characters.", path
        )
    description = manifest.get("description")
    if isinstance(description, str) and len(description) > 200:
        result.add(
            "error", "manifest.description-length", "description exceeds 200 characters.", path
        )

    sprite_value = manifest.get("spritesheetPath")
    if not isinstance(sprite_value, str):
        return None
    sprite_rel = Path(sprite_value)
    if sprite_rel.is_absolute() or ".." in sprite_rel.parts or len(sprite_rel.parts) != 1:
        result.add(
            "error",
            "manifest.unsafe-spritesheet-path",
            "spritesheetPath must be a single safe filename in the pet directory.",
            path,
        )
        return None
    if sprite_rel.suffix.lower() not in {".png", ".webp"}:
        result.add("error", "manifest.sprite-format", "Spritesheet must be PNG or WebP.", path)
    return result.pet_dir / sprite_rel


def _metadata_checks(result: ValidationResult) -> dict[str, Any] | None:
    path = result.pet_dir / "pet.meta.json"
    if path.is_symlink():
        result.add("error", "metadata.symlink", "pet.meta.json must not be a symlink.", path)
        return None
    try:
        metadata = load_json(path)
    except CatalogError as exc:
        result.add("error", "metadata.invalid", str(exc), path)
        return None

    missing = sorted(REQUIRED_METADATA_FIELDS - set(metadata))
    if missing:
        result.add(
            "error",
            "metadata.missing-fields",
            f"Missing required metadata fields: {', '.join(missing)}.",
            path,
        )
    unknown = sorted(set(metadata) - ALLOWED_METADATA_FIELDS)
    if unknown:
        result.add(
            "error",
            "metadata.unknown-fields",
            f"Unknown metadata fields: {', '.join(unknown)}.",
            path,
        )
    schema_ref = metadata.get("$schema")
    if schema_ref is not None and not isinstance(schema_ref, str):
        result.add("error", "metadata.schema-ref", "$schema must be a string when present.", path)

    if type(metadata.get("schemaVersion")) is not int or metadata.get("schemaVersion") != 1:
        result.add("error", "metadata.schema-version", "schemaVersion must be 1.", path)
    version = metadata.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        result.add("error", "metadata.version", "version must be semantic version text.", path)

    authors = metadata.get("authors")
    if not isinstance(authors, list) or not authors:
        result.add("error", "metadata.authors", "Declare at least one author.", path)
    elif any(
        not isinstance(item, dict)
        or not isinstance(item.get("name"), str)
        or not item["name"].strip()
        for item in authors
    ):
        result.add("error", "metadata.authors", "Every author needs a non-empty name.", path)
    else:
        for author in authors:
            unknown_author_fields = sorted(set(author) - {"name", "url"})
            if unknown_author_fields:
                result.add(
                    "error",
                    "metadata.author-fields",
                    f"Unknown author fields: {', '.join(unknown_author_fields)}.",
                    path,
                )
            if "url" in author and not isinstance(author["url"], str):
                result.add("error", "metadata.author-url", "Author url must be a string.", path)

    license_name = metadata.get("assetLicense")
    if not isinstance(license_name, str) or not license_name.strip():
        result.add(
            "error", "metadata.asset-license", "Declare the pet asset license or notice.", path
        )

    checksum = metadata.get("spritesheetSha256")
    if not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum):
        result.add(
            "error",
            "metadata.spritesheet-sha256",
            "spritesheetSha256 must be a lowercase 64-character SHA-256 digest.",
            path,
        )

    tags = metadata.get("tags")
    if (
        not isinstance(tags, list)
        or any(not isinstance(tag, str) or not tag.strip() for tag in tags)
        or len(tags) != len(set(tags))
    ):
        result.add(
            "error",
            "metadata.tags",
            "tags must be a list of unique, non-empty strings.",
            path,
        )

    provenance = metadata.get("provenance")
    if not isinstance(provenance, dict):
        result.add("error", "metadata.provenance", "Declare structured asset provenance.", path)
    else:
        for key in ("aiAssisted", "thirdPartyCharacter", "redistributionConfirmed"):
            if not isinstance(provenance.get(key), bool):
                result.add(
                    "error",
                    "metadata.provenance",
                    f"provenance.{key} must be true or false.",
                    path,
                )
        if provenance.get("redistributionConfirmed") is not True:
            result.add(
                "error",
                "metadata.redistribution-not-confirmed",
                "provenance.redistributionConfirmed must be true before submission.",
                path,
            )

    tested_with = metadata.get("testedWith")
    if (
        not isinstance(tested_with, dict)
        or not isinstance(tested_with.get("codexDesktop"), str)
        or not tested_with["codexDesktop"].strip()
    ):
        result.add(
            "error",
            "metadata.tested-with",
            "testedWith.codexDesktop must be a non-empty version string.",
            path,
        )

    for filename, code in (
        ("LICENSE-ASSETS.md", "metadata.asset-notice"),
        ("README.md", "metadata.readme"),
    ):
        required_path = result.pet_dir / filename
        if not required_path.is_file():
            result.add("error", code, f"Missing {filename}.", result.pet_dir)
        elif required_path.is_symlink():
            result.add(
                "error", f"{code}-symlink", f"{filename} must not be a symlink.", required_path
            )

    required_previews = ["preview/contact-sheet.png"]
    required_previews.extend(
        f"preview/{row.index:02d}-{row.state}.gif"
        for row in ANIMATION_ROWS
        if row.durations_ms is not None
    )
    for relative in required_previews:
        preview_path = result.pet_dir / relative
        if not preview_path.is_file():
            result.add(
                "warning",
                "preview.missing",
                f"Missing committed preview file {relative}.",
                preview_path,
            )
        elif preview_path.is_symlink():
            result.add(
                "error", "preview.symlink", f"{relative} must not be a symlink.", preview_path
            )
    return metadata


def _count_hidden_rgb(image: Image.Image) -> int:
    count = 0
    for red, green, blue, alpha in image.get_flattened_data():
        if alpha == 0 and (red or green or blue):
            count += 1
    return count


def _atlas_checks(result: ValidationResult, sprite_path: Path) -> None:
    if not sprite_path.is_file():
        result.add("error", "atlas.missing", "Spritesheet file does not exist.", sprite_path)
        return
    if sprite_path.is_symlink():
        result.add("error", "atlas.symlink", "Spritesheet must not be a symlink.", sprite_path)
        return
    size = sprite_path.stat().st_size
    if size > MAX_SPRITESHEET_BYTES:
        result.add(
            "error", "atlas.too-large", "Spritesheet exceeds the 20 MiB app limit.", sprite_path
        )
        return

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(sprite_path) as source:
                if source.size != (ATLAS_WIDTH, ATLAS_HEIGHT):
                    result.add(
                        "error",
                        "atlas.dimensions",
                        f"Expected {ATLAS_WIDTH}x{ATLAS_HEIGHT}; "
                        f"found {source.width}x{source.height}.",
                        sprite_path,
                    )
                    return
                source.load()
                if source.format not in {"PNG", "WEBP"}:
                    result.add(
                        "error",
                        "atlas.format",
                        "Spritesheet must decode as PNG or WebP.",
                        sprite_path,
                    )
                if "A" not in source.getbands() and "transparency" not in source.info:
                    result.add(
                        "error", "atlas.alpha", "Spritesheet needs an alpha channel.", sprite_path
                    )
                image = source.convert("RGBA")
    except (
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        result.add("error", "atlas.decode", f"Could not decode spritesheet: {exc}", sprite_path)
        return

    for row in ANIMATION_ROWS:
        top = row.index * CELL_HEIGHT
        for column in range(COLUMNS):
            box = (
                column * CELL_WIDTH,
                top,
                (column + 1) * CELL_WIDTH,
                top + CELL_HEIGHT,
            )
            alpha = image.crop(box).getchannel("A")
            if is_used_cell(row, column):
                bbox = alpha.getbbox()
                if bbox is None:
                    result.add(
                        "error",
                        "atlas.empty-used-cell",
                        f"{row.state} frame {column} is empty.",
                        sprite_path,
                    )
                elif (
                    bbox[0] <= 1
                    or bbox[1] <= 1
                    or bbox[2] >= CELL_WIDTH - 1
                    or bbox[3] >= CELL_HEIGHT - 1
                ):
                    result.add(
                        "warning",
                        "atlas.near-edge",
                        f"{row.state} frame {column} is within one pixel of a cell edge.",
                        sprite_path,
                    )
            elif alpha.getbbox() is not None:
                result.add(
                    "error",
                    "atlas.nonempty-unused-cell",
                    f"Unused {row.state} frame slot {column} must be transparent.",
                    sprite_path,
                )

    hidden_rgb = _count_hidden_rgb(image)
    if hidden_rgb:
        result.add(
            "error",
            "atlas.hidden-rgb",
            f"Found {hidden_rgb} fully transparent pixels with non-zero RGB residue.",
            sprite_path,
        )


def validate_pet(pet_dir: Path, *, strict: bool = False) -> ValidationResult:
    pet_dir = pet_dir.resolve()
    result = ValidationResult(pet_id=pet_dir.name, pet_dir=pet_dir)
    manifest_path = pet_dir / "pet.json"
    sprite_path: Path | None = None
    try:
        manifest = load_json(manifest_path)
    except CatalogError as exc:
        result.add("error", "manifest.invalid", str(exc), manifest_path)
    else:
        sprite_path = _manifest_checks(result, manifest, manifest_path)

    metadata = _metadata_checks(result)
    if sprite_path is not None:
        _atlas_checks(result, sprite_path)
        if metadata is not None and sprite_path.is_file():
            actual = hashlib.sha256(sprite_path.read_bytes()).hexdigest()
            expected = metadata.get("spritesheetSha256")
            if expected != actual:
                result.add(
                    "error",
                    "metadata.spritesheet-sha256-mismatch",
                    f"spritesheetSha256 must be {actual} for the current file.",
                    result.pet_dir / "pet.meta.json",
                )

    if strict:
        for issue in tuple(result.issues):
            if issue.severity == "warning":
                result.issues.remove(issue)
                result.add("error", f"strict.{issue.code}", issue.message, issue.path)
    return result
