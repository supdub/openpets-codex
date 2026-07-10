from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any


class CatalogError(RuntimeError):
    pass


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _pets_root(repo_root: Path) -> tuple[Path, Path]:
    pets_path = repo_root / "pets"
    if pets_path.is_symlink():
        raise CatalogError(f"Refusing symlinked pets directory: {pets_path}")
    pets_root = pets_path.resolve()
    if not pets_root.is_dir():
        raise CatalogError(f"Missing pets directory: {pets_path}")
    resolved_repo_root = repo_root.resolve()
    if not _is_within(pets_root, resolved_repo_root):
        raise CatalogError(f"Pets directory must stay inside the repository: {pets_root}")
    return pets_path, pets_root


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "pets").is_dir():
            return candidate
    package_root = Path(__file__).resolve().parents[2]
    if (package_root / "pets").is_dir():
        return package_root
    raise CatalogError("Could not find a repository root containing pyproject.toml and pets/.")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CatalogError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CatalogError(f"Expected a JSON object in {path}.")
    return value


def pet_directories(repo_root: Path) -> list[Path]:
    pets_path, pets_root = _pets_root(repo_root)
    directories: list[Path] = []
    for path in pets_path.iterdir():
        if path.is_symlink():
            raise CatalogError(f"Refusing symlinked catalog entry: {path}")
        resolved = path.resolve()
        if not _is_within(resolved, pets_root):
            raise CatalogError(f"Catalog entry must stay inside {pets_root}: {resolved}")
        if (
            not path.name.startswith(".")
            and resolved.is_dir()
            and (resolved / "pet.json").is_file()
        ):
            directories.append(path)
    return sorted(directories)


def resolve_pet(repo_root: Path, value: str | Path) -> Path:
    _, pets_root = _pets_root(repo_root)
    raw = Path(value)
    candidate = raw if raw.is_absolute() or raw.exists() else repo_root / "pets" / raw
    if candidate.is_symlink():
        raise CatalogError(f"Refusing symlinked pet directory: {candidate}")
    resolved = candidate.resolve()
    if not _is_within(resolved, pets_root):
        raise CatalogError(f"Pet path must stay inside {pets_root}: {resolved}")
    if not resolved.is_dir():
        raise CatalogError(f"Pet not found: {value}")
    return resolved


def choose_pet_directories(
    repo_root: Path, values: Iterable[str] | None = None, *, all_pets: bool = False
) -> list[Path]:
    chosen = list(values or [])
    if all_pets or not chosen:
        return pet_directories(repo_root)
    return [resolve_pet(repo_root, value) for value in chosen]
