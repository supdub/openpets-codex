# Installing pets

## One-click install

The repository README provides a `codex://pets/install` link pinned to a version tag. Codex
downloads the direct HTTPS WebP, validates its content type, size, dimensions, and sprite version,
then asks before installing it. A browser or policy may block custom-protocol links; the catalog
CLI below is the portable fallback. One-click installs are app-managed and may use a different
local folder name, so `openpets doctor` applies only to catalog-CLI installs. Use the same method
for later updates.

## Recommended: catalog CLI

```bash
git clone https://github.com/supdub/openpets-codex.git
cd openpets-codex
python -m venv .venv
```

Activate the environment, then install:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
openpets list
openpets install hoshino-ai
```

```bash
# macOS or Linux
source .venv/bin/activate
python -m pip install -e .
openpets list
openpets install hoshino-ai
```

The command validates the pet, stages it next to the destination, and atomically installs only
`pet.json` plus the referenced spritesheet. It honors `CODEX_HOME`; use `--codex-home` to override
the location.

In Codex Desktop:

1. Open **Settings → Pets**.
2. Choose **Refresh**.
3. Select the custom pet.
4. Choose **Wake Pet**, or type `/pet`.

Check the local copy at any time:

```bash
openpets doctor hoshino-ai
```

To update, pull the repository and reinstall with `--force`. To remove the pet, run
`openpets uninstall hoshino-ai`.

## Manual install

Copy only a pet's `pet.json` and `spritesheet.webp` into:

```text
~/.codex/pets/<pet-id>/
```

On Windows that is normally `C:\Users\<you>\.codex\pets\<pet-id>\`. Keep the directory name equal
to the `id` in `pet.json`, then use **Settings → Pets → Refresh**.

## Windows and WSL

Running the installer in WSL without an override targets the Linux home, which Windows Codex does
not read. Prefer PowerShell. If you must use WSL:

```bash
openpets install hoshino-ai --codex-home /mnt/c/Users/<windows-user>/.codex
```

## Troubleshooting

- **Pet does not appear:** run `openpets validate <id> --strict`, confirm the directory name, then
  choose Refresh.
- **Wrong dimensions:** new desktop pets are v2 and require `1536x2288` plus
  `spriteVersionNumber: 2`.
- **Pet still looks old:** run `openpets doctor <id>` and reinstall with `--force`.
- **Different Codex home:** set `CODEX_HOME` or pass `--codex-home`.
- **Overlay is asleep:** choose Wake Pet or type `/pet`.
