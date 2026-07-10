# Repository guidance

OpenPets for Codex is a static pet catalog plus a Python validation/install tool.

## Invariants

- New desktop pets use `spriteVersionNumber: 2`.
- The final atlas is `1536x2288`, arranged as 8 columns by 11 rows of `192x208` cells.
- Runtime `pet.json` contains only the five app fields documented in `docs/PET_FORMAT.md`.
- Repository-only author, version, license, provenance, and compatibility data belongs in
  `pet.meta.json`.
- Never treat third-party character rights as open-source merely because an image is generated
  or redrawn.
- Installers copy only `pet.json` and its spritesheet into the user's Codex home.

## Before finishing a change

```bash
ruff check .
ruff format --check .
pytest
openpets validate --all --strict --check-registry
```

If a spritesheet changes, also run `openpets preview <id>` and visually inspect the contact sheet
and every state GIF. Preserve unrelated user changes and do not edit files under `~/.codex`
unless the task explicitly includes local installation testing.
