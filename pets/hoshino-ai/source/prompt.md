# Generation brief

## Identity

A tasteful, non-sexualized chibi pixel-art fan depiction of Ai Hoshino: long deep-violet hair with
soft magenta gradient tips, large six-pointed star pupils, a cheerful idol expression, and a compact
pink, red, and white stage outfit. The face, hair ornament, microphone, palette, proportions, and
silhouette remain stable across all states.

## Rendering

- Crisp hand-pixeled 16-bit game sprite aesthetic.
- Chunky compact silhouette and limited palette.
- Hard stepped edges, simple dark outline, flat cel shading, and no antialiasing.
- Designed to remain readable inside a `192x208` cell.
- Generated on a flat `#00FF00` key, then deterministically extracted and despilled.

## State constraints

Rows follow `docs/PET_FORMAT.md`. No text, scenery, grid, cast shadow, glow, detached icons, speed
lines, dust, or neighboring-pose overlap. Active work is a focused working pose rather than literal
running. Look directions rotate gaze/head mechanics clockwise without rotating the whole body.

## Tool provenance

Generated with Codex's built-in OpenAI image generation path and assembled with the deterministic
Codex hatch-pet v2 tools bundled in Codex Desktop 26.707.3748.0. No image reference was supplied
for the base design.
