from __future__ import annotations

import json

from openpets.registry import registry_matches, write_registry
from tests.helpers import make_pet


def test_registry_is_deterministic_and_detects_drift(tmp_path) -> None:
    make_pet(tmp_path)
    path = write_registry(tmp_path)
    assert registry_matches(tmp_path)
    value = json.loads(path.read_text(encoding="utf-8"))
    value["pets"][0]["displayName"] = "Drifted"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert not registry_matches(tmp_path)
