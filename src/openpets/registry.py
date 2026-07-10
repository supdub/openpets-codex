from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openpets.catalog import load_json, pet_directories


def build_registry(repo_root: Path) -> dict[str, Any]:
    entries = []
    for pet_dir in pet_directories(repo_root):
        manifest = load_json(pet_dir / "pet.json")
        metadata = load_json(pet_dir / "pet.meta.json")
        entries.append(
            {
                "id": manifest["id"],
                "displayName": manifest["displayName"],
                "description": manifest["description"],
                "version": metadata["version"],
                "path": f"pets/{pet_dir.name}",
                "preview": f"pets/{pet_dir.name}/preview/00-idle.gif",
                "tags": metadata.get("tags", []),
                "assetLicense": metadata["assetLicense"],
                "spritesheetSha256": metadata["spritesheetSha256"],
            }
        )
    return {"schemaVersion": 1, "pets": sorted(entries, key=lambda item: item["id"])}


def registry_matches(repo_root: Path) -> bool:
    path = repo_root / "pets.json"
    if not path.is_file():
        return False
    expected = build_registry(repo_root)
    if load_json(path) != expected:
        return False
    return all((repo_root / entry["preview"]).is_file() for entry in expected["pets"])


def write_registry(repo_root: Path) -> Path:
    path = repo_root / "pets.json"
    path.write_text(
        json.dumps(build_registry(repo_root), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path
