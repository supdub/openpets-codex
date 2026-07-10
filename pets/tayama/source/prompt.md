# Generation brief

## Identity

A tasteful, non-sexualized chibi pixel fan depiction of adult Tayama: burgundy-red bobbed hair
with blunt bangs, longer face-framing locks and a small low side/back tie; red eyes; a dark
navy-black studded biker jacket over a pale mint-white sleeveless mini dress; black choker and belt
with restrained brass hardware; smoky-brown tights; and white ankle boots. Her relaxed confidence,
knowing side-glance, costume, palette, proportions, and silhouette remain stable across all states.

## Scene and smoking motif

- One lit cigarette stays visibly in hand, with a small orange ember.
- Smoke is a thin, hard-edged, continuous curl attached to the cigarette or mouth, never a detached
  cloud.
- The stationary rows include an inhale, ember pulse, exhale, restrained side-eye, and subtle
  weight shifts.
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

## State constraints

Rows follow `docs/PET_FORMAT.md`: calm smoking idle, right and left travel, free-hand wave,
five-stage jump, failed slump and recovery, expectant waiting, focused active work, satisfied
review, and a clockwise 16-direction look loop. Row 0 column 6 contains the neutral look frame.
Every used frame preserves the character, cigarette, scene orientation, scale, and safe padding;
unused cells are fully transparent.

## Tool provenance

Generated with Codex's built-in OpenAI image generation path from text prompts and assembled with
deterministic local Pillow-based tooling. Official character images, manga panels, animation
frames, extracted sprites, and traced art were not supplied as image inputs. Official title and
character pages were consulted only to write the textual design description and rights notice.
