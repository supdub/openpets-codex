# Testing

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the same checks as CI:

```bash
ruff check .
ruff format --check .
pytest
openpets validate --all --strict --check-registry
```

For a changed pet, also run `openpets preview <id>` and inspect the output. Use a temporary Codex
home for a safe installer smoke test:

```bash
openpets install <id> --codex-home .work/test-codex-home
openpets doctor <id> --codex-home .work/test-codex-home
openpets uninstall <id> --codex-home .work/test-codex-home
```

PNG/GIF encoder bytes can differ by operating system even when the atlas is identical. Run
`openpets preview --all --check` to compare the committed files with a temporary fresh render.
The check requires an exact decoded contact sheet plus matching GIF geometry, frames, timing, and
loop metadata; it allows only the small measured pixel variation caused by platform quantization.
CI runs this semantic check and a separate smoke render on both Windows and Linux.
