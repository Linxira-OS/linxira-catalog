#!/usr/bin/env python3
"""Re-label catalog offlinePolicy from the actual offline package set.

The catalog's offlinePolicy was hand-maintained and diverged from what the
ISO actually ships (offline-repo has 800+ packages; only 3 items were marked
"included"). This script re-computes the label from the real offline package
list: if every package a leaf needs is present in the offline set, the leaf is
installable offline and must be marked "included".

Usage:
    python3 scripts/sync-offline-policy.py catalog/catalog-v3.json offline-packages.txt [--write]

The offline package list is produced on the builder by:
    ls <iso>/opt/linxira/offline-repo/x86_64/*.pkg.tar.zst |
        xargs -n1 basename | sed 's/-[0-9][0-9.]*.*//' | sort -u
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_package_set(path: Path) -> set[str]:
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        name = line.strip()
        if name and not name.startswith("#"):
            names.add(name)
    return names


def leaf_packages(item: dict) -> list[str]:
    """All package ids the leaf needs (artifact ids + requires)."""
    artifact = item.get("artifact") or {}
    ids = list(artifact.get("ids") or [])
    ids += list(item.get("requires") or [])
    return [p for p in ids if isinstance(p, str)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("packages", type=Path)
    parser.add_argument("--write", action="store_true",
                        help="write changes back to the catalog file")
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    offline = load_package_set(args.packages)

    changed: list[tuple[str, str, str]] = []
    for section in ("desktops", "applications", "components"):
        for item in catalog.get(section, []):
            leaf_id = item.get("id")
            packages = leaf_packages(item)
            availability = item.setdefault("availability", {})
            old_policy = availability.get("offlinePolicy", "online-only")
            if not packages:
                continue
            missing = [p for p in packages if p not in offline]
            if not missing:
                new_policy = "included"
                availability["networkRequired"] = False
            else:
                new_policy = "online-only"
                availability["networkRequired"] = True
            if new_policy != old_policy:
                availability["offlinePolicy"] = new_policy
                changed.append((str(leaf_id), old_policy, new_policy))

    if not changed:
        print("no changes needed")
        return 0

    print(f"relabeled {len(changed)} items:")
    for leaf_id, old, new in changed:
        print(f"  {leaf_id}: {old} -> {new}")

    if args.write:
        args.catalog.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("written:", args.catalog)
    else:
        print("(dry run; pass --write to persist)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
