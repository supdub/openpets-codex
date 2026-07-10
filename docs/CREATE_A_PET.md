# Creating a pet

## 1. Scaffold the package

```bash
openpets scaffold my-pet --display-name "My Pet" --description "A friendly companion." --author "Your name" --asset-license "CC-BY-4.0"
```

The command creates manifests, a source folder, asset notice, and `source/atlas-guide.png`. The
guide is not a valid final spritesheet. Save the finished `spritesheet.webp` beside `pet.json`, not
inside `source/`.

## 2. Design for a 192x208 cell

Use a compact full-body silhouette, readable face, stable palette, and generous padding. Lock the
character design before animating. Pixel, vector, plush, clay, painterly, and 3D styles all work if
they remain clear at pet size and preserve transparent edges.

Create rows 0-8 from the state table in [PET_FORMAT.md](PET_FORMAT.md). Treat active work
(`running`) as concentration or processing, not literal travel. Make waiting, failed, work, and
review visibly distinct. Idle animation uses row 0 columns 0-5; put the required neutral look pose
in row 0 column 6.

Rows 9-10 form one clockwise 16-pose look loop. Establish unmistakable up, right, down, and left
anchors, interpolate the diagonals evenly, and do not rotate the entire sprite just to fake gaze.

## 3. Export cleanly

Export a transparent lossless WebP at exactly `1536x2288`. Empty standard-row cells must be fully
transparent (row 0 column 6 is required, not empty). Clear hidden RGB beneath alpha zero and keep
every pose inside its own cell.

## 4. Add provenance and terms

Complete `pet.meta.json` and `LICENSE-ASSETS.md`. Record editable sources, palette, prompts, and
export steps under `source/`. Never commit private or unlicensed reference images.

## 5. Preview and validate

```bash
openpets preview my-pet
openpets validate my-pet --strict
openpets registry
pytest
```

Inspect the contact sheet plus each GIF at normal pet size. Automated geometry cannot catch a
wrong-facing run, identity drift, static loop, awkward pop, or ambiguous look direction.

## 6. Test in Codex

```bash
openpets install my-pet --force
```

Use Settings → Pets → Refresh, select it, wake it, and exercise idle, active work, waiting, review,
and failed states before opening a pull request.
