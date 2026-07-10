from __future__ import annotations

import hashlib
import json

import pytest

from openpets.install import InstallError, install_pet, installation_matches, uninstall_pet
from tests.helpers import make_pet


def test_install_doctor_and_uninstall(tmp_path) -> None:
    pet_dir = make_pet(tmp_path / "repo")
    codex_home = tmp_path / "codex-home"
    destination = install_pet(pet_dir, codex_home)
    assert sorted(path.name for path in destination.iterdir()) == ["pet.json", "spritesheet.webp"]
    assert installation_matches(pet_dir, codex_home)[0]
    uninstall_pet("test-pet", codex_home)
    assert not destination.exists()


def test_install_refuses_overwrite(tmp_path) -> None:
    pet_dir = make_pet(tmp_path / "repo")
    codex_home = tmp_path / "codex-home"
    install_pet(pet_dir, codex_home)
    try:
        install_pet(pet_dir, codex_home)
    except InstallError as exc:
        assert "--force" in str(exc)
    else:
        raise AssertionError("Expected overwrite refusal")


def test_uninstall_rejects_path_traversal_even_with_force(tmp_path) -> None:
    codex_home = tmp_path / "codex-home"
    victim = tmp_path / "victim"
    victim.mkdir()
    marker = victim / "keep.txt"
    marker.write_text("safe", encoding="utf-8")

    try:
        uninstall_pet("../../victim", codex_home, force=True)
    except InstallError as exc:
        assert "kebab-case" in str(exc) or "escapes" in str(exc)
    else:
        raise AssertionError("Expected traversal refusal")
    assert marker.read_text(encoding="utf-8") == "safe"


def test_uninstall_rejects_absolute_path_even_with_force(tmp_path) -> None:
    codex_home = tmp_path / "codex-home"
    victim = tmp_path / "victim"
    victim.mkdir()

    try:
        uninstall_pet(str(victim), codex_home, force=True)
    except InstallError as exc:
        assert "kebab-case" in str(exc)
    else:
        raise AssertionError("Expected absolute-path refusal")
    assert victim.is_dir()


def test_custom_safe_spritesheet_filename_round_trip(tmp_path) -> None:
    pet_dir = make_pet(tmp_path / "repo")
    original = pet_dir / "spritesheet.webp"
    custom = pet_dir / "ai.webp"
    original.rename(custom)
    manifest_path = pet_dir / "pet.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["spritesheetPath"] = custom.name
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    metadata_path = pet_dir / "pet.meta.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["spritesheetSha256"] = hashlib.sha256(custom.read_bytes()).hexdigest()
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    codex_home = tmp_path / "codex-home"
    destination = install_pet(pet_dir, codex_home)
    assert (destination / "ai.webp").is_file()
    uninstall_pet("test-pet", codex_home)
    assert not destination.exists()


def test_uninstall_rejects_symlinked_pets_root(tmp_path) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    outside = tmp_path / "outside"
    installed = outside / "test-pet"
    installed.mkdir(parents=True)
    (installed / "pet.json").write_text(
        json.dumps(
            {
                "id": "test-pet",
                "displayName": "Test Pet",
                "description": "fixture",
                "spriteVersionNumber": 2,
                "spritesheetPath": "spritesheet.webp",
            }
        ),
        encoding="utf-8",
    )
    marker = installed / "spritesheet.webp"
    marker.write_bytes(b"keep")
    try:
        (codex_home / "pets").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"Directory symlinks unavailable: {exc}")

    with pytest.raises(InstallError, match="symlink"):
        uninstall_pet("test-pet", codex_home)
    assert marker.read_bytes() == b"keep"
