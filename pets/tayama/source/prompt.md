# Generation brief

## Identity

A tasteful, non-sexualized chibi pixel fan depiction of adult Tayama: burgundy-red bobbed hair
with blunt bangs, longer face-framing locks and a small low side/back tie; red eyes; a dark
navy-black studded biker jacket over a pale mint-white sleeveless mini dress; black choker and belt
with restrained brass hardware; smoky-brown tights; and white ankle boots. Her relaxed confidence,
knowing side-glance, costume, palette, proportions, and silhouette remain stable across all states.

## Scene and smoking motif

- The 6.6-second idle loop keeps Tayama seated in all six animated frames and tells a complete,
  repeatable cigarette story: a relaxed exhale, inhale with ember pulse and blink, ash tap with a
  visibly shorter cigarette, final-stub exhale, a newly lit full cigarette, and a long first draw
  that flows back into the opening pose. Roughly 5.76 seconds are lit-smoking beats, followed by a
  0.84-second relight beat that completes the 6.6-second cycle.
- Whenever present, the cigarette stays physically attached to the intended hand or mouth. The
  lighter appears only during ignition, and flame appears only where it touches the cigarette tip.
- Smoke is a thin, hard-edged, continuous curl attached to the cigarette or mouth, never a detached
  cloud.
- Idle, hover, waiting, and task completion use one settled seated anchor with planted hips, stable
  head scale, crossed legs, and a consistent boot baseline. Expressive motion comes from the ember,
  smoke curl, blink, ash tap, ankle flex, jacket-hand motion, side-eye, and restrained free-hand
  gestures rather than repeated sitting and standing.
- A compact generic nighttime supermarket rear-service vignette stays inside the sprite footprint:
  gray metal service door and wall, tiny fluorescent lamp, narrow blue service panel, yellow crate,
  tall metal ashtray, and a small pavement base.
- The vignette contains no text, trademarks, supermarket branding, or cigarette-brand artwork and
  leaves transparent padding on every side.

## Rendering

- Crisp hand-pixeled 16-bit adventure-game sprite aesthetic and limited nocturnal palette.
- Compact chibi silhouette, dark stepped outline, flat cel shading, and no motion blur.
- Designed to remain readable inside a `192x208` cell.
- Generated on a flat green chroma key, extracted into registered frame slots, edge-despilled,
  alpha-hardened for clean pixel edges and GIF previews, and assembled as a lossless RGBA WebP.
- Idle, hover, waiting, and completion foregrounds are composited over one identical locked
  supermarket plate, so the door, lamp, blue panel, crate, ashtray, steps, and pavement remain
  pixel-still while Tayama changes pose.

## State constraints

Rows follow `docs/PET_FORMAT.md`: the six-frame idle is an uninterrupted seated smoking and
relighting performance; right and left travel remain unchanged; the greeting row keeps its
free-hand wave; the technical `jumping` row is deliberately illustrated as a planted five-frame
seated mouse-hover wave with no jump; failed keeps its standing slump and recovery; waiting is a
closed six-frame seated expectant loop; active work remains focused and standing; review is a
planted six-frame seated task-completion wave that settles back to its opening pose; and the final
two rows contain the clockwise 16-direction look loop. Cigarette placement and attached smoke
remain consistent through the seated hover, waiting, and completion gestures.

Row 0 column 6 retains a dedicated standing neutral look frame. The fixed v2 atlas has no
persistent sit/stand mode flag. Idle, technical `jumping`/hover, waiting, and review share the
settled seated anchor; drag travel, greeting, failure and recovery, active work, the neutral look,
and directional tracking retain their contextual standing poses. Every used frame preserves the
character, locked supermarket scene, scale, and safe padding; unused cells are fully transparent.

## Tool provenance

Generated with Codex's built-in OpenAI image generation path from text prompts and assembled with
deterministic local Pillow-based tooling. Official character images, manga panels, animation
frames, extracted sprites, and traced art were not supplied as image inputs. Official title and
character pages were consulted only to write the textual design description and rights notice.
