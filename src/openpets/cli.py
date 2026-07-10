from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openpets.catalog import (
    CatalogError,
    choose_pet_directories,
    find_repo_root,
    load_json,
    pet_directories,
    resolve_pet,
)
from openpets.install import InstallError, install_pet, installation_matches, uninstall_pet
from openpets.preview import PreviewError, check_previews, render_previews
from openpets.registry import registry_matches, write_registry
from openpets.scaffold import ScaffoldError, scaffold_pet
from openpets.validate import validate_pet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openpets", description="Manage native Codex pets.")
    parser.add_argument("--repo", type=Path, help="Repository root (normally auto-detected).")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List pets in the catalog.")

    validate = subparsers.add_parser("validate", help="Validate one pet or the whole catalog.")
    validate.add_argument("pets", nargs="*")
    validate.add_argument("--all", action="store_true", dest="all_pets")
    validate.add_argument("--strict", action="store_true")
    validate.add_argument("--json", action="store_true", dest="json_output")
    validate.add_argument("--check-registry", action="store_true")

    install = subparsers.add_parser("install", help="Install a pet into Codex Desktop.")
    install.add_argument("pet")
    install.add_argument("--codex-home", type=Path)
    install.add_argument("--force", action="store_true")

    uninstall = subparsers.add_parser("uninstall", help="Remove an installed custom pet.")
    uninstall.add_argument("pet_id")
    uninstall.add_argument("--codex-home", type=Path)
    uninstall.add_argument("--force", action="store_true")

    doctor = subparsers.add_parser("doctor", help="Compare an installed pet with the catalog.")
    doctor.add_argument("pet")
    doctor.add_argument("--codex-home", type=Path)

    preview = subparsers.add_parser("preview", help="Render a contact sheet and animation GIFs.")
    preview.add_argument("pet", nargs="?")
    preview.add_argument("--all", action="store_true", dest="all_pets")
    preview.add_argument("--output", type=Path)
    preview.add_argument("--check", action="store_true")

    scaffold = subparsers.add_parser("scaffold", help="Create a new contributor pet folder.")
    scaffold.add_argument("pet_id")
    scaffold.add_argument("--display-name", required=True)
    scaffold.add_argument("--description", required=True)
    scaffold.add_argument("--author", required=True)
    scaffold.add_argument("--asset-license", default="CC-BY-4.0")

    registry = subparsers.add_parser("registry", help="Regenerate or check pets.json.")
    registry.add_argument("--check", action="store_true")
    return parser


def _repo(args: argparse.Namespace) -> Path:
    return args.repo.resolve() if args.repo else find_repo_root()


def _print_validation(result: object) -> None:
    pet_id = result.pet_id
    print(f"{'PASS' if result.ok else 'FAIL'}  {pet_id}")
    for issue in result.issues:
        print(f"  {issue.severity.upper():7} {issue.code}: {issue.message}")


def run(args: argparse.Namespace) -> int:
    repo = _repo(args)
    if args.command == "list":
        rows = []
        for pet_dir in pet_directories(repo):
            manifest = load_json(pet_dir / "pet.json")
            metadata = load_json(pet_dir / "pet.meta.json")
            rows.append((manifest["id"], manifest["displayName"], metadata["version"]))
        if not rows:
            print("No pets found.")
            return 0
        width = max(len(row[0]) for row in rows)
        for pet_id, name, version in rows:
            print(f"{pet_id:<{width}}  {name}  v{version}")
        return 0

    if args.command == "validate":
        directories = choose_pet_directories(repo, args.pets, all_pets=args.all_pets)
        results = [validate_pet(path, strict=args.strict) for path in directories]
        registry_ok = not args.check_registry or registry_matches(repo)
        if args.json_output:
            print(
                json.dumps(
                    {
                        "ok": all(result.ok for result in results) and registry_ok,
                        "registryOk": registry_ok,
                        "results": [result.to_dict() for result in results],
                    },
                    indent=2,
                )
            )
        else:
            for result in results:
                _print_validation(result)
            if args.check_registry:
                print(f"{'PASS' if registry_ok else 'FAIL'}  pets.json registry")
        return 0 if all(result.ok for result in results) and registry_ok else 1

    if args.command == "install":
        pet_dir = resolve_pet(repo, args.pet)
        destination = install_pet(pet_dir, args.codex_home, force=args.force)
        print(f"Installed {pet_dir.name} to {destination}")
        print(
            "In Codex, open Settings > Pets, click Refresh, select the pet, then choose Wake Pet."
        )
        return 0

    if args.command == "uninstall":
        destination = uninstall_pet(args.pet_id, args.codex_home, force=args.force)
        print(f"Removed {destination}")
        return 0

    if args.command == "doctor":
        pet_dir = resolve_pet(repo, args.pet)
        ok, message = installation_matches(pet_dir, args.codex_home)
        print(f"{'PASS' if ok else 'FAIL'}  {message}")
        return 0 if ok else 1

    if args.command == "preview":
        if args.check and args.output is not None:
            raise CatalogError("--check cannot be combined with --output.")
        if args.all_pets:
            directories = pet_directories(repo)
        elif args.pet:
            directories = [resolve_pet(repo, args.pet)]
        else:
            raise CatalogError("Pass a pet id or --all.")
        if args.check:
            all_current = True
            for pet_dir in directories:
                current, messages = check_previews(pet_dir)
                print(f"{'PASS' if current else 'FAIL'}  {pet_dir.name} previews")
                for message in messages:
                    print(f"  {message}")
                all_current = all_current and current
            return 0 if all_current else 1
        for pet_dir in directories:
            output = args.output / pet_dir.name if args.output and args.all_pets else args.output
            for path in render_previews(pet_dir, output):
                print(path)
        return 0

    if args.command == "scaffold":
        destination = scaffold_pet(
            repo,
            args.pet_id,
            args.display_name,
            args.description,
            author=args.author,
            asset_license=args.asset_license,
        )
        print(f"Created {destination}")
        print(
            "Next: use source/atlas-guide.png as a guide, then save the final transparent "
            "atlas beside pet.json as spritesheet.webp."
        )
        return 0

    if args.command == "registry":
        if args.check:
            ok = registry_matches(repo)
            print(f"{'PASS' if ok else 'FAIL'}  pets.json registry")
            return 0 if ok else 1
        print(write_registry(repo))
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (CatalogError, InstallError, PreviewError, ScaffoldError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
