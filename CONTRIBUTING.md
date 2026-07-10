# Contributing

Thanks for helping make Codex a little more alive. First contributions are welcome, including a
single pet, documentation improvement, validation rule, or small bug fix.

## Development setup

```bash
git clone https://github.com/supdub/openpets-codex.git
cd openpets-codex
python -m venv .venv
```

Activate it with `.\.venv\Scripts\Activate.ps1` on Windows PowerShell or
`source .venv/bin/activate` on macOS/Linux, then run:

```bash
python -m pip install -e ".[dev]"
pytest
```

## Submit a pet

1. Read [the format contract](docs/PET_FORMAT.md) and [art workflow](docs/CREATE_A_PET.md).
2. Run `openpets scaffold <id> --display-name ... --description ... --author ...`.
3. Add a lossless `spritesheet.webp`, source notes, and previews.
4. Complete `pet.meta.json` and `LICENSE-ASSETS.md` honestly.
5. Run `openpets preview <id>` and inspect every state.
6. Run `openpets registry`, then the checks below.
7. Open a pull request using the template.

Pet IDs use lowercase kebab case and must match the folder and runtime manifest. Keep editable
source and prompt notes under `source/`; never commit credentials, private reference images, or
generated caches.

## Required checks

```bash
ruff check .
ruff format --check .
pytest
openpets validate --all --strict --check-registry
openpets preview --all --check
```

Automated checks cannot judge animation quality. Review the generated contact sheet and GIFs for
identity drift, wrong direction, clipping, frame popping, shadows, detached effects, or a static
idle loop.

## Rights and provenance

By submitting assets, you confirm that you created them or have permission to redistribute them
under the declared terms. Say whether the work is original, commissioned, or AI-assisted and
whether a third-party character is depicted. Do not submit traced art, leaked assets, screenshots,
logos, or copyrighted references you cannot redistribute.

Fan content is reviewed case by case and must have a clear notice. Maintainers may reject or
remove content when rights are unclear. Read [ASSET_POLICY.md](ASSET_POLICY.md).

## Pull request size

Prefer one pet or one focused tool change per pull request. Avoid Git LFS for ordinary pet files;
the app limit is 20 MiB and the validator enforces it.
