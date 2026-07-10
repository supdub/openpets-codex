# Architecture

Codex Desktop owns rendering, the floating overlay, state transitions, selection, and persistence.
OpenPets supplies only validated static packages and contributor tooling.

```text
pets/<id> ──validate──> v2 contract ──atomic install──> ~/.codex/pets/<id>
     │                                                   │
     ├── preview/contact sheet                           └── Codex Settings → Pets → Refresh
     ├── repository metadata
     └── per-asset license
```

The runtime boundary is deliberately narrow: the installer copies `pet.json` and one spritesheet.
There is no injected JavaScript, Electron overlay, background daemon, or arbitrary per-pet code.
That keeps contributions reviewable and lets the Codex app remain the authority for behavior.

`pet.meta.json`, previews, source notes, schemas, and licenses stay in the repository and are not
installed. `pets.json` is a deterministic catalog index checked in CI.
