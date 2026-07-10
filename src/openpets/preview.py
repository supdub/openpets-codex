from __future__ import annotations

import os
import uuid
import warnings
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw

from openpets.catalog import load_json
from openpets.contract import (
    ANIMATION_ROWS,
    ATLAS_HEIGHT,
    ATLAS_WIDTH,
    CELL_HEIGHT,
    CELL_WIDTH,
    COLUMNS,
    MAX_SPRITESHEET_BYTES,
    is_used_cell,
)


class PreviewError(RuntimeError):
    pass


_GIF_DIFFERING_PIXEL_FRACTION = 0.02
_GIF_RGBA_MEAN_ERROR = 1.0
_GIF_RGB_CHANNEL_MEAN_ERROR = 1.0
_GIF_ALPHA_MEAN_ERROR = 2.0
_GIF_ALPHA_MASK_MISMATCH_FRACTION = 0.01


def _atomic_save(image: Image.Image, path: Path, **save_options: object) -> None:
    if path.is_symlink():
        raise PreviewError(f"Refusing to overwrite symlinked preview target: {path}")
    temporary = path.parent / f".{path.stem}.{uuid.uuid4().hex}{path.suffix}"
    try:
        image.save(temporary, **save_options)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _checkerboard(size: tuple[int, int], square: int = 12) -> Image.Image:
    image = Image.new("RGBA", size, (238, 240, 245, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                draw.rectangle((x, y, x + square - 1, y + square - 1), fill=(211, 216, 226, 255))
    return image


def render_previews(pet_dir: Path, output_dir: Path | None = None) -> list[Path]:
    pet_dir = pet_dir.resolve()
    manifest = load_json(pet_dir / "pet.json")
    sprite_value = manifest.get("spritesheetPath")
    if not isinstance(sprite_value, str):
        raise PreviewError("spritesheetPath must be a string.")
    sprite_rel = Path(sprite_value)
    if sprite_rel.is_absolute() or ".." in sprite_rel.parts or len(sprite_rel.parts) != 1:
        raise PreviewError("spritesheetPath must be one safe filename in the pet directory.")
    sprite_path = pet_dir / sprite_rel
    if sprite_path.is_symlink() or sprite_path.resolve().parent != pet_dir:
        raise PreviewError("Refusing to preview a symlinked or escaping spritesheet.")
    if not sprite_path.is_file():
        raise PreviewError(f"Spritesheet does not exist: {sprite_path}")
    if sprite_path.stat().st_size > MAX_SPRITESHEET_BYTES:
        raise PreviewError("Spritesheet exceeds the 20 MiB app limit.")

    if output_dir is None:
        output = pet_dir / "preview"
        if output.is_symlink() or output.resolve().parent != pet_dir:
            raise PreviewError("Default preview directory must stay inside the pet directory.")
    else:
        output = output_dir.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(sprite_path) as source:
                if source.size != (ATLAS_WIDTH, ATLAS_HEIGHT):
                    raise PreviewError(
                        f"Expected {ATLAS_WIDTH}x{ATLAS_HEIGHT}; "
                        f"found {source.width}x{source.height}."
                    )
                source.load()
                atlas = source.convert("RGBA")
    except (
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise PreviewError(f"Could not decode spritesheet safely: {exc}") from exc

    padding = 16
    label_width = 170
    sheet_width = label_width + COLUMNS * CELL_WIDTH + padding * 2
    sheet_height = len(ANIMATION_ROWS) * CELL_HEIGHT + padding * 2
    sheet = _checkerboard((sheet_width, sheet_height))
    draw = ImageDraw.Draw(sheet)
    written: list[Path] = []
    for row in ANIMATION_ROWS:
        top = row.index * CELL_HEIGHT
        draw.text((padding, padding + top + 8), f"{row.index}: {row.state}", fill=(24, 28, 36, 255))
        frames: list[Image.Image] = []
        for column in range(COLUMNS):
            box = (
                column * CELL_WIDTH,
                top,
                (column + 1) * CELL_WIDTH,
                top + CELL_HEIGHT,
            )
            frame = atlas.crop(box)
            if is_used_cell(row, column):
                sheet.alpha_composite(
                    frame, (label_width + padding + column * CELL_WIDTH, padding + top)
                )
            if column < row.frames:
                frames.append(frame)
        if row.durations_ms:
            gif_path = output / f"{row.index:02d}-{row.state}.gif"
            _atomic_save(
                frames[0],
                gif_path,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=list(row.durations_ms),
                loop=0,
                disposal=2,
            )
            written.append(gif_path)

    sheet_path = output / "contact-sheet.png"
    _atomic_save(sheet.convert("RGB"), sheet_path, format="PNG", optimize=True)
    written.insert(0, sheet_path)
    return written


def _committed_preview_directory(pet_dir: Path) -> Path:
    preview_dir = pet_dir / "preview"
    if preview_dir.is_symlink():
        raise PreviewError("Refusing to check a symlinked committed preview directory.")
    try:
        resolved = preview_dir.resolve()
    except OSError as exc:
        raise PreviewError(f"Could not resolve committed preview directory safely: {exc}") from exc
    if resolved.parent != pet_dir:
        raise PreviewError("Committed preview directory must stay inside the pet directory.")
    return preview_dir


def _decode_static_rgba(path: Path) -> Image.Image:
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError(
                    f"expected a PNG container, found {image.format or 'unknown format'}"
                )
            image.load()
            return image.convert("RGBA")


def _decode_gif(
    path: Path,
) -> tuple[tuple[int, int], int, tuple[int | None, ...], int | None, list[Image.Image]]:
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as image:
            if image.format != "GIF":
                raise ValueError(
                    f"expected a GIF container, found {image.format or 'unknown format'}"
                )
            size = image.size
            frame_count = getattr(image, "n_frames", 1)
            loop = image.info.get("loop")
            durations: list[int | None] = []
            frames: list[Image.Image] = []
            for frame_index in range(frame_count):
                image.seek(frame_index)
                durations.append(image.info.get("duration"))
                frames.append(image.convert("RGBA").copy())
    return size, frame_count, tuple(durations), loop, frames


def _frame_difference_metrics(
    generated: Image.Image, committed: Image.Image
) -> tuple[int, float, tuple[float, float, float], float, int, int]:
    generated_bytes = generated.tobytes()
    committed_bytes = committed.tobytes()
    different_pixels = 0
    channel_totals = [0, 0, 0, 0]
    alpha_mask_mismatches = 0
    max_pixel_delta = 0

    for offset in range(0, len(generated_bytes), 4):
        deltas = tuple(
            abs(generated_bytes[offset + channel] - committed_bytes[offset + channel])
            for channel in range(4)
        )
        if any(deltas):
            different_pixels += 1
        for channel, delta in enumerate(deltas):
            channel_totals[channel] += delta
        if (generated_bytes[offset + 3] == 0) != (committed_bytes[offset + 3] == 0):
            alpha_mask_mismatches += 1
        max_pixel_delta = max(max_pixel_delta, *deltas)

    pixels = generated.width * generated.height
    channel_means = tuple(total / pixels for total in channel_totals)
    overall_mean = sum(channel_totals) / (pixels * 4)
    return (
        different_pixels,
        overall_mean,
        (channel_means[0], channel_means[1], channel_means[2]),
        channel_means[3],
        alpha_mask_mismatches,
        max_pixel_delta,
    )


def _compare_contact_sheet(generated: Path, committed: Path) -> list[str]:
    try:
        generated_image = _decode_static_rgba(generated)
        committed_image = _decode_static_rgba(committed)
    except (
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        return [f"contact-sheet.png: could not decode preview safely: {exc}"]

    if generated_image.size != committed_image.size:
        return [
            "contact-sheet.png: decoded size mismatch "
            f"(committed {committed_image.width}x{committed_image.height}, "
            f"generated {generated_image.width}x{generated_image.height})."
        ]
    if generated_image.tobytes() == committed_image.tobytes():
        return []

    different_pixels = sum(
        generated_pixel != committed_pixel
        for generated_pixel, committed_pixel in zip(
            generated_image.get_flattened_data(),
            committed_image.get_flattened_data(),
            strict=True,
        )
    )
    return [
        "contact-sheet.png: decoded pixels differ exactly at "
        f"{different_pixels}/{generated_image.width * generated_image.height} pixels."
    ]


def _compare_gif(generated: Path, committed: Path) -> list[str]:
    name = generated.name
    try:
        generated_data = _decode_gif(generated)
        committed_data = _decode_gif(committed)
    except (
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        return [f"{name}: could not decode GIF safely: {exc}"]

    generated_size, generated_count, generated_durations, generated_loop, generated_frames = (
        generated_data
    )
    committed_size, committed_count, committed_durations, committed_loop, committed_frames = (
        committed_data
    )
    messages: list[str] = []
    if committed_size != generated_size:
        messages.append(
            f"{name}: dimensions mismatch "
            f"(committed {committed_size[0]}x{committed_size[1]}, "
            f"generated {generated_size[0]}x{generated_size[1]})."
        )
    if committed_count != generated_count:
        messages.append(
            f"{name}: frame count mismatch "
            f"(committed {committed_count}, generated {generated_count})."
        )
    if committed_durations != generated_durations:
        messages.append(
            f"{name}: per-frame durations mismatch "
            f"(committed {committed_durations}, generated {generated_durations})."
        )
    if committed_loop != generated_loop:
        messages.append(
            f"{name}: loop mismatch (committed {committed_loop}, generated {generated_loop})."
        )

    if committed_size != generated_size:
        return messages

    pixels = generated_size[0] * generated_size[1]
    differing_limit = ceil(pixels * _GIF_DIFFERING_PIXEL_FRACTION)
    alpha_mask_limit = ceil(pixels * _GIF_ALPHA_MASK_MISMATCH_FRACTION)
    for frame_index, (generated_frame, committed_frame) in enumerate(
        zip(generated_frames, committed_frames, strict=False)
    ):
        (
            different_pixels,
            rgba_mean,
            rgb_means,
            alpha_mean,
            alpha_mask_mismatches,
            max_pixel_delta,
        ) = _frame_difference_metrics(generated_frame, committed_frame)
        failures: list[str] = []
        if different_pixels > differing_limit:
            failures.append(
                f"differing pixels {different_pixels}/{pixels} exceed {differing_limit}"
            )
        if rgba_mean > _GIF_RGBA_MEAN_ERROR:
            failures.append(f"RGBA mean error {rgba_mean:.3f} exceeds 1.000")
        for channel, mean in zip("RGB", rgb_means, strict=True):
            if mean > _GIF_RGB_CHANNEL_MEAN_ERROR:
                failures.append(f"{channel} mean error {mean:.3f} exceeds 1.000")
        if alpha_mean > _GIF_ALPHA_MEAN_ERROR:
            failures.append(f"alpha mean error {alpha_mean:.3f} exceeds 2.000")
        if alpha_mask_mismatches > alpha_mask_limit:
            failures.append(
                f"alpha-mask mismatches {alpha_mask_mismatches}/{pixels} exceed {alpha_mask_limit}"
            )
        if failures:
            messages.append(
                f"{name} frame {frame_index}: "
                + "; ".join(failures)
                + f"; max single-pixel delta {max_pixel_delta} (diagnostic only)."
            )
    return messages


def check_previews(pet_dir: Path) -> tuple[bool, list[str]]:
    pet_dir = pet_dir.resolve()
    committed_dir = _committed_preview_directory(pet_dir)
    with TemporaryDirectory(prefix=f"openpets-{pet_dir.name}-preview-") as temporary:
        generated_dir = Path(temporary)
        generated_paths = render_previews(pet_dir, generated_dir)
        generated_names = {path.name for path in generated_paths}

        if not committed_dir.exists():
            return False, [f"preview filename set mismatch: missing {sorted(generated_names)}."]
        if not committed_dir.is_dir():
            return False, ["Committed preview path is not a directory."]
        try:
            committed_entries = list(committed_dir.iterdir())
        except OSError as exc:
            raise PreviewError(
                f"Could not inspect committed preview directory safely: {exc}"
            ) from exc
        for entry in committed_entries:
            if entry.is_symlink():
                raise PreviewError(
                    f"Refusing to check symlinked committed preview artifact: {entry}"
                )

        committed_names = {entry.name for entry in committed_entries}
        missing = sorted(generated_names - committed_names)
        unexpected = sorted(committed_names - generated_names)
        messages: list[str] = []
        if missing or unexpected:
            details = []
            if missing:
                details.append(f"missing {missing}")
            if unexpected:
                details.append(f"unexpected {unexpected}")
            messages.append("preview filename set mismatch: " + "; ".join(details) + ".")

        for name in sorted(generated_names & committed_names):
            generated = generated_dir / name
            committed = committed_dir / name
            if not committed.is_file():
                messages.append(f"{name}: committed preview entry is not a regular file.")
                continue
            if name == "contact-sheet.png":
                messages.extend(_compare_contact_sheet(generated, committed))
            elif name.endswith(".gif"):
                messages.extend(_compare_gif(generated, committed))
            else:
                messages.append(f"{name}: unsupported generated preview type.")
    return not messages, messages
