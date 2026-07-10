# Codex v2 pet format

Each catalog entry has repository metadata and a two-file runtime package:

```text
pets/<pet-id>/
├── pet.json              # copied to Codex
├── spritesheet.webp      # copied to Codex
├── pet.meta.json         # repository provenance/version data
├── LICENSE-ASSETS.md     # artwork terms and notices
├── README.md
├── preview/
└── source/
```

## Runtime manifest

The OpenPets catalog deliberately requires `pet.json` to contain exactly five fields:

```json
{
  "id": "my-pet",
  "displayName": "My Pet",
  "description": "One short sentence.",
  "spriteVersionNumber": 2,
  "spritesheetPath": "spritesheet.webp"
}
```

The current app keys custom pets by folder and can infer an internal identity without `id`, but the
catalog requires an explicit lowercase kebab-case ID so installs, updates, registry entries, and
uninstalls are deterministic. The spritesheet path is one local PNG or WebP filename; paths, URLs,
and traversal are rejected.

## Atlas geometry

- Canvas: `1536x2288`
- Grid: 8 columns × 11 rows
- Cell: `192x208`
- Background: transparent
- Fully transparent pixels: RGB must also be zero

| Row | State | Used columns | Timing / order |
| ---: | --- | ---: | --- |
| 0 | idle + neutral look | 0-6 | animation uses 0-5 at authored 280, 110, 110, 140, 140, 320 ms (Codex plays these ×6); column 6 is the neutral look frame |
| 1 | running-right | 0-7 | 120 ms each; last 220 ms |
| 2 | running-left | 0-7 | 120 ms each; last 220 ms |
| 3 | waving | 0-3 | 140 ms each; last 280 ms |
| 4 | jumping | 0-4 | 140 ms each; last 280 ms |
| 5 | failed | 0-7 | 140 ms each; last 240 ms |
| 6 | waiting | 0-5 | 150 ms each; last 260 ms |
| 7 | running / active work | 0-5 | 120 ms each; last 220 ms |
| 8 | review / ready | 0-5 | 150 ms each; last 280 ms |
| 9 | look directions A | 0-7 | 000 through 157.5 degrees clockwise |
| 10 | look directions B | 0-7 | 180 through 337.5 degrees clockwise |

Unused cells in rows 0-8 are fully transparent, except the required neutral look frame at row 0,
column 6. Every cell in rows 9-10 is used. `000` means looking up (12 o'clock), not
neutral/front; Codex uses row 0, column 6 while directional tracking is inactive.

The preview generator uses the effective idle durations (`1680, 660, 660, 840, 840, 1920 ms`) so
the committed GIF matches the slower cadence seen in Codex Desktop.

## Visual acceptance

The same identity, silhouette, palette, outfit, props, scale, and baseline should survive every
row. Directional motion must face correctly, look directions progress clockwise, and the first
idle frame works as a reduced-motion still. Avoid text, scenery, detached effects, shadows, glow,
clipping, neighboring-cell bleed, and effectively duplicated frames.
