from __future__ import annotations

import shutil

import pytest

from openpets.cli import main
from openpets.scaffold import ScaffoldError, scaffold_pet
from tests.helpers import make_pet


def test_cli_list_and_validate(tmp_path, capsys) -> None:
    make_pet(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    assert main(["--repo", str(tmp_path), "list"]) == 0
    assert "test-pet" in capsys.readouterr().out
    assert main(["--repo", str(tmp_path), "validate", "--all"]) == 0


def _symlink_directory_or_skip(link, target) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Directory symlinks unavailable: {exc}")


def test_scaffold_rejects_symlinked_pets_root_without_external_writes(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    outside = tmp_path / "outside"
    repo_root.mkdir()
    outside.mkdir()
    _symlink_directory_or_skip(repo_root / "pets", outside)

    with pytest.raises(ScaffoldError, match="symlinked pets directory"):
        scaffold_pet(
            repo_root,
            "unsafe-pet",
            "Unsafe Pet",
            "Must not be created outside the repository.",
            author="Tests",
            asset_license="CC0-1.0",
        )

    assert list(outside.iterdir()) == []


def test_scaffold_rejects_escaping_symlinked_destination(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    pets_root = repo_root / "pets"
    outside = tmp_path / "outside"
    pets_root.mkdir(parents=True)
    outside.mkdir()
    _symlink_directory_or_skip(pets_root / "unsafe-pet", outside)

    with pytest.raises(ScaffoldError, match="must stay inside the repository"):
        scaffold_pet(
            repo_root,
            "unsafe-pet",
            "Unsafe Pet",
            "Must not follow an escaping destination.",
            author="Tests",
            asset_license="CC0-1.0",
        )

    assert list(outside.iterdir()) == []


def test_preview_all_rejects_symlinked_pet_without_external_previews(tmp_path, capsys) -> None:
    repo_root = tmp_path / "repo"
    (repo_root / "pets").mkdir(parents=True)
    external_pet = make_pet(tmp_path / "external", pet_id="external-pet")
    shutil.rmtree(external_pet / "preview")
    _symlink_directory_or_skip(repo_root / "pets" / "external-pet", external_pet)

    assert main(["--repo", str(repo_root), "preview", "--all"]) == 2
    assert "symlinked catalog entry" in capsys.readouterr().err
    assert not (external_pet / "preview").exists()
