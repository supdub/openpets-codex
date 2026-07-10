# Generation brief

## Identity

A respectful chibi pixel caricature of Sam Altman: short cropped silver-gray hair, clean-shaven
face, blue-gray eyes, dark navy crewneck sweater, charcoal trousers, and white-gray sneakers. The
signature resting silhouette is a balanced, dignified one-knee-down kneel. Stationary states keep
that identity while directional travel uses a compact crouched shuffle.

## Rendering

- Crisp hand-pixeled 16-bit game-sprite aesthetic and limited cool palette.
- Chunky compact silhouette, dark stepped outline, flat cel shading, and no antialiasing.
- Respectful editorial caricature with no logos, captions, mockery, or official imagery.
- Designed to remain readable inside a `192x208` cell.
- Generated on a flat `#00FF00` key, then deterministically extracted and despilled.

## State constraints

Rows follow `docs/PET_FORMAT.md`. No text, scenery, grid, cast shadow, glow, detached icons, speed
lines, dust, props, or neighboring-pose overlap. Active work is a focused kneeling pose. Look
directions rotate gaze and head mechanics clockwise while the kneeling body stays stable.

## Tool provenance

Generated with Codex's built-in OpenAI image generation path and assembled with the deterministic
Codex hatch-pet v2 tools bundled in Codex Desktop 26.707.3748.0. No image reference was supplied
for the base design.
