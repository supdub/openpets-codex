# Compatibility

## Native desktop package

This repository targets Codex Desktop's v2 local pet package:

- `spriteVersionNumber: 2`
- `1536x2288` lossless PNG or WebP atlas
- 8 columns by 11 rows
- installation under `${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/`

The first catalog release is tested against Codex Desktop `26.707.3748.0` on Windows. The format
is app-owned and may evolve; update this file, the schemas, validator, and tests together when it
does.

## Web upload

Some web surfaces document the older 8x9 (`1536x1872`) upload format. The v2 desktop package is
the source of truth here. Contributors may crop rows 0-8 for a separate web artifact, but must
never package that cropped file as a new desktop v2 pet.

## WSL

Codex Desktop on Windows reads the Windows user's `.codex` directory. Run `openpets install` from
PowerShell, or pass `--codex-home /mnt/c/Users/<name>/.codex` when using the CLI inside WSL.
