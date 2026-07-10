# OpenPets for Codex

Community-made animated companions for the native Codex desktop pet system.

This repository is intentionally small and contributor-first: each pet is a self-contained
folder, the Python tool explains validation failures in plain language, and CI checks the same
package that Codex loads locally.

> [!IMPORTANT]
> OpenPets for Codex is an independent community project. It is not affiliated with or endorsed
> by OpenAI, the unrelated OpenPets project, or the owners of any third-party characters.

## Included pets

| Pet | Preview | Notes |
| --- | --- | --- |
| **Pixel 星野爱** (`hoshino-ai`) | See [`pets/hoshino-ai`](pets/hoshino-ai) | Unofficial, AI-assisted fan art; separate asset terms apply. |
| **Kneeling Sam Altman** (`sam-altman`) | See [`pets/sam-altman`](pets/sam-altman) | Unofficial public-figure caricature; separate likeness terms apply. |
| **Pixel Makise Kurisu** (`makise-kurisu`) | See [`pets/makise-kurisu`](pets/makise-kurisu) | Unofficial, AI-assisted fan art; separate asset terms apply. |
| **Pixel Tayama** (`tayama`) | See [`pets/tayama`](pets/tayama) | Unofficial, AI-assisted fan art; separate asset terms apply. |

## Install a pet

### One click (Codex Desktop)

[Install Pixel 星野爱 in Codex](codex://pets/install?name=Pixel+%E6%98%9F%E9%87%8E%E7%88%B1&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fsupdub%2Fopenpets-codex%2Fv0.2.0%2Fpets%2Fhoshino-ai%2Fspritesheet.webp&description=An+unofficial+fan-made+pixel+idol+companion+with+starry+eyes.&spriteVersionNumber=2)

[Install Kneeling Sam Altman in Codex](codex://pets/install?name=Kneeling+Sam+Altman&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fsupdub%2Fopenpets-codex%2Fv0.2.0%2Fpets%2Fsam-altman%2Fspritesheet.webp&description=An+unofficial+pixel+caricature+of+Sam+Altman%2C+thoughtfully+kneeling+between+coding+tasks.&spriteVersionNumber=2)

[Install Pixel Makise Kurisu in Codex](codex://pets/install?name=Pixel+Makise+Kurisu&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fsupdub%2Fopenpets-codex%2Fv0.2.0%2Fpets%2Fmakise-kurisu%2Fspritesheet.webp&description=An+unofficial+fan-made+pixel+scientist+companion+inspired+by+Makise+Kurisu.&spriteVersionNumber=2)

The links are pinned to the `v0.2.0` tag. Codex previews and validates a package before installing
it. App-managed one-click installs may use an app-derived local folder name, so `openpets doctor`
is intended for CLI installs. Use the same method to update a pet. If your browser does not open
custom links, use the catalog CLI below.

### Catalog CLI

You need Python 3.10 or newer.

```bash
git clone https://github.com/supdub/openpets-codex.git
cd openpets-codex
python -m venv .venv
```

Activate the environment and install the small CLI:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
openpets list
openpets install sam-altman  # Replace with any listed pet ID.
```

```bash
# macOS or Linux
source .venv/bin/activate
python -m pip install -e .
openpets list
openpets install sam-altman  # Replace with any listed pet ID.
```

Then open **Codex Settings → Pets**, choose **Refresh**, select the pet, and choose **Wake Pet**.
You can also type `/pet` in Codex. See [the full installation guide](docs/INSTALL.md) for manual
copying, WSL, updates, and troubleshooting.

## Add your own pet

```bash
python -m pip install -e ".[dev]"
openpets scaffold my-pet --display-name "My Pet" --description "A tiny companion for long coding sessions." --author "Your name"
```

Use the generated `source/atlas-guide.png` as a layout guide, save the final
`spritesheet.webp` beside `pet.json`, update the asset notice and provenance, then run:

```bash
openpets preview my-pet
openpets validate my-pet --strict
pytest
```

Start with [Creating a pet](docs/CREATE_A_PET.md), then read [CONTRIBUTING.md](CONTRIBUTING.md).
No application code change is required to submit a new pet.

## Useful commands

| Command | Purpose |
| --- | --- |
| `openpets list` | Show the catalog. |
| `openpets validate --all --strict --check-registry` | Run the CI-grade checks. |
| `openpets preview <id>` | Build a contact sheet and animation GIFs. |
| `openpets preview --all --check` | Verify committed previews match fresh renders. |
| `openpets install <id>` | Atomically install a validated pet. |
| `openpets doctor <id>` | Confirm the installed files match the repository. |
| `openpets uninstall <id>` | Remove a custom pet safely. |
| `openpets scaffold <id> ...` | Start a contribution from a guide. |
| `openpets registry` | Regenerate `pets.json`. |

## Project scope

The repository targets the native Codex desktop v2 spritesheet contract. It does not patch
Codex, inject UI, run background services, or add custom interaction hooks. See
[the architecture](docs/ARCHITECTURE.md) and [compatibility policy](COMPATIBILITY.md).

Code and documentation are MIT licensed. Pet artwork has per-pet terms and does **not**
automatically inherit the code license; see [ASSET_POLICY.md](ASSET_POLICY.md).
