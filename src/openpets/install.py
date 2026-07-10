from __future__ import annotations

import json
import os
import re
import shutil
import uuid
from pathlib import Path

from openpets.catalog import load_json
from openpets.validate import validate_pet

PET_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class InstallError(RuntimeError):
    pass


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def _safe_pet_destination(codex_home: Path, pet_id: str) -> tuple[Path, Path]:
    if not PET_ID.fullmatch(pet_id):
        raise InstallError("Pet id must be a lowercase kebab-case slug.")
    home = codex_home.expanduser().resolve()
    raw_pets_root = home / "pets"
    if raw_pets_root.is_symlink():
        raise InstallError("Codex pets directory must not be a symlink.")
    pets_root = raw_pets_root.resolve()
    if pets_root.parent != home:
        raise InstallError("Codex pets directory escapes the configured Codex home.")
    destination = pets_root / pet_id
    if destination.parent.resolve() != pets_root:
        raise InstallError("Pet destination escapes the Codex pets directory.")
    return pets_root, destination


def install_pet(pet_dir: Path, codex_home: Path | None = None, *, force: bool = False) -> Path:
    pet_dir = pet_dir.resolve()
    validation = validate_pet(pet_dir)
    if not validation.ok:
        detail = "; ".join(issue.message for issue in validation.errors)
        raise InstallError(f"Refusing to install an invalid pet: {detail}")

    manifest = load_json(pet_dir / "pet.json")
    pet_id = str(manifest["id"])
    sprite_name = str(manifest["spritesheetPath"])
    home = (codex_home or default_codex_home()).expanduser().resolve()
    pets_root, destination = _safe_pet_destination(home, pet_id)
    pets_root.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise InstallError(f"Refusing to replace symlinked pet directory: {destination}")
    if destination.exists() and not force:
        raise InstallError(f"{destination} already exists; pass --force to replace it.")

    staging = pets_root / f".{pet_id}.staging-{uuid.uuid4().hex}"
    backup = pets_root / f".{pet_id}.backup-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        shutil.copy2(pet_dir / "pet.json", staging / "pet.json")
        shutil.copy2(pet_dir / sprite_name, staging / sprite_name)
        if destination.exists():
            destination.rename(backup)
        staging.rename(destination)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        if backup.exists() and not destination.exists():
            backup.rename(destination)
        raise
    return destination


def uninstall_pet(pet_id: str, codex_home: Path | None = None, *, force: bool = False) -> Path:
    home = (codex_home or default_codex_home()).expanduser().resolve()
    _, destination = _safe_pet_destination(home, pet_id)
    if destination.is_symlink():
        raise InstallError(f"Refusing to remove symlinked pet directory: {destination}")
    if not destination.is_dir():
        raise InstallError(f"Pet is not installed: {pet_id}")
    manifest_path = destination / "pet.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        if not force:
            raise InstallError(
                "Installed pet manifest is unreadable; pass --force to remove."
            ) from exc
        manifest = {}
    if manifest.get("id") != pet_id and not force:
        raise InstallError(
            "Installed manifest id does not match the folder; pass --force to remove."
        )
    allowed_files = {"pet.json"}
    sprite_name = manifest.get("spritesheetPath")
    sprite_path = Path(sprite_name) if isinstance(sprite_name, str) else None
    if (
        sprite_path is not None
        and not sprite_path.is_absolute()
        and ".." not in sprite_path.parts
        and len(sprite_path.parts) == 1
        and sprite_path.suffix.lower() in {".png", ".webp"}
    ):
        allowed_files.add(sprite_path.name)
    elif not force:
        raise InstallError("Installed spritesheetPath is unsafe; pass --force to remove.")
    unknown = {item.name for item in destination.iterdir()} - allowed_files
    if unknown and not force:
        raise InstallError(
            f"Installed directory has unknown files ({', '.join(sorted(unknown))}); pass --force."
        )
    shutil.rmtree(destination)
    return destination


def installation_matches(pet_dir: Path, codex_home: Path | None = None) -> tuple[bool, str]:
    manifest = load_json(pet_dir / "pet.json")
    home = (codex_home or default_codex_home()).expanduser().resolve()
    _, installed = _safe_pet_destination(home, str(manifest["id"]))
    if not installed.is_dir():
        return False, f"not installed at {installed}"
    for filename in ("pet.json", str(manifest["spritesheetPath"])):
        source = pet_dir / filename
        target = installed / filename
        if not target.is_file() or source.read_bytes() != target.read_bytes():
            return False, f"installed {filename} differs from the repository"
    return True, f"installed files match at {installed}"
