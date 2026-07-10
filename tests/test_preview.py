from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from openpets.cli import main
from openpets.contract import CELL_HEIGHT, CELL_WIDTH
from openpets.preview import PreviewError, check_previews, render_previews
from tests.helpers import make_pet

REPO_ROOT = Path(__file__).resolve().parents[1]


def _preview_snapshot(preview_dir: Path) -> dict[str, tuple[bytes, int]]:
    return {
        path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in preview_dir.iterdir()
    }


def test_preview_rejects_escaping_spritesheet_path(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    outside = tmp_path / "outside.webp"
    outside.write_bytes((pet_dir / "spritesheet.webp").read_bytes())
    manifest_path = pet_dir / "pet.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["spritesheetPath"] = "../outside.webp"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    try:
        render_previews(pet_dir)
    except PreviewError as exc:
        assert "safe filename" in str(exc)
    else:
        raise AssertionError("Expected unsafe preview path refusal")


def test_preview_rejects_symlinked_output_target(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    outside = tmp_path / "outside.gif"
    outside.write_bytes(b"keep")
    target = pet_dir / "preview" / "00-idle.gif"
    target.unlink()
    try:
        target.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"File symlinks unavailable: {exc}")

    with pytest.raises(PreviewError, match="symlinked preview target"):
        render_previews(pet_dir)
    assert outside.read_bytes() == b"keep"


def test_current_committed_previews_are_semantically_current() -> None:
    pet_dirs = sorted(path for path in (REPO_ROOT / "pets").iterdir() if path.is_dir())
    assert pet_dirs
    for pet_dir in pet_dirs:
        current, messages = check_previews(pet_dir)
        assert current, f"{pet_dir.name}:\n" + "\n".join(messages)


def test_rendered_gif_preserves_adaptive_transparency_index(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    spritesheet = pet_dir / "spritesheet.webp"
    with Image.open(spritesheet) as source:
        atlas = source.convert("RGBA")
    draw = ImageDraw.Draw(atlas)
    for column in range(6):
        left = column * CELL_WIDTH
        draw.rectangle(
            (left, 0, left + CELL_WIDTH - 1, CELL_HEIGHT - 1),
            fill=(0, 0, 0, 0),
        )
        draw.rectangle(
            (left + 24, 24, left + 167, 183),
            fill=(220 - column * 10, 80 + column * 10, 160, 255),
        )
    atlas.save(spritesheet, format="WEBP", lossless=True, method=6)

    render_previews(pet_dir)

    with Image.open(pet_dir / "preview" / "00-idle.gif") as idle:
        assert idle.n_frames == 6
        for frame_index in range(idle.n_frames):
            idle.seek(frame_index)
            rgba = idle.convert("RGBA")
            assert rgba.getpixel((0, 0))[3] == 0
            assert rgba.getpixel((96, 104))[3] == 255


def test_check_previews_rejects_one_pixel_contact_sheet_change(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    contact_sheet = pet_dir / "preview" / "contact-sheet.png"
    with Image.open(contact_sheet) as source:
        changed = source.convert("RGB")
    red, green, blue = changed.getpixel((0, 0))
    changed.putpixel((0, 0), ((red + 1) % 256, green, blue))
    changed.save(contact_sheet, format="PNG")

    current, messages = check_previews(pet_dir)

    assert not current
    assert any("contact-sheet.png: decoded pixels differ" in message for message in messages)


def test_check_previews_rejects_mislabeled_contact_sheet_container(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    contact_sheet = pet_dir / "preview" / "contact-sheet.png"
    with Image.open(contact_sheet) as source:
        replacement = source.convert("RGB")
    replacement.save(contact_sheet, format="BMP")

    current, messages = check_previews(pet_dir)

    assert not current
    assert any("expected a PNG container" in message for message in messages)


def test_check_previews_rejects_missing_gif(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    missing = pet_dir / "preview" / "00-idle.gif"
    missing.unlink()

    current, messages = check_previews(pet_dir)

    assert not current
    assert any(
        "filename set mismatch" in message and "00-idle.gif" in message for message in messages
    )


def test_check_previews_rejects_wrong_gif(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    wrong = pet_dir / "preview" / "00-idle.gif"
    first = Image.new("RGBA", (8, 8), (255, 0, 0, 255))
    second = Image.new("RGBA", (8, 8), (0, 0, 255, 255))
    first.save(
        wrong,
        format="GIF",
        save_all=True,
        append_images=[second],
        duration=[10, 10],
        loop=1,
    )

    current, messages = check_previews(pet_dir)

    assert not current
    assert any("00-idle.gif: dimensions mismatch" in message for message in messages)
    assert any("00-idle.gif: frame count mismatch" in message for message in messages)


def test_check_previews_rejects_mislabeled_gif_container(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    wrong = pet_dir / "preview" / "00-idle.gif"
    Image.new("RGBA", (192, 208), (255, 0, 0, 255)).save(wrong, format="PNG")

    current, messages = check_previews(pet_dir)

    assert not current
    assert any("expected a GIF container" in message for message in messages)


def test_check_previews_rejects_symlinked_committed_directory(tmp_path) -> None:
    pet_dir = make_pet(tmp_path)
    preview_dir = pet_dir / "preview"
    outside = tmp_path / "outside-preview"
    shutil.move(preview_dir, outside)
    try:
        preview_dir.symlink_to(outside, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Directory symlinks unavailable: {exc}")

    with pytest.raises(PreviewError, match="symlinked committed preview directory"):
        check_previews(pet_dir)


def test_cli_preview_check_is_non_mutating(tmp_path, capsys) -> None:
    pet_dir = make_pet(tmp_path)
    preview_dir = pet_dir / "preview"
    before = _preview_snapshot(preview_dir)

    assert main(["--repo", str(tmp_path), "preview", "test-pet", "--check"]) == 0

    assert "PASS  test-pet previews" in capsys.readouterr().out
    assert _preview_snapshot(preview_dir) == before


def test_cli_preview_check_returns_one_for_stale_preview_without_repairing_it(
    tmp_path, capsys
) -> None:
    pet_dir = make_pet(tmp_path)
    preview_dir = pet_dir / "preview"
    (preview_dir / "00-idle.gif").unlink()
    before = _preview_snapshot(preview_dir)

    assert main(["--repo", str(tmp_path), "preview", "test-pet", "--check"]) == 1

    output = capsys.readouterr().out
    assert "FAIL  test-pet previews" in output
    assert "preview filename set mismatch" in output
    assert _preview_snapshot(preview_dir) == before
    assert not (preview_dir / "00-idle.gif").exists()


def test_cli_preview_check_rejects_output(tmp_path, capsys) -> None:
    make_pet(tmp_path)
    output = tmp_path / "separate-output"

    assert (
        main(
            [
                "--repo",
                str(tmp_path),
                "preview",
                "test-pet",
                "--check",
                "--output",
                str(output),
            ]
        )
        == 2
    )

    assert "--check cannot be combined with --output" in capsys.readouterr().err
    assert not output.exists()
