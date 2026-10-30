"""Resolve logical module names to local paths and TFE registry sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tf_factory.policy import repo_root_from


def default_catalog_path(root: Path | None = None) -> Path:
    root = root or repo_root_from()
    return root / "factory" / "catalog.yaml"


def load_catalog(catalog_path: Path | None = None) -> dict[str, Any]:
    path = catalog_path or default_catalog_path()
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or "modules" not in data:
        raise ValueError(f"Invalid catalog file: {path}")
    return data


def tfe_source(catalog: dict[str, Any], logical_name: str) -> str:
    modules = catalog["modules"]
    if logical_name not in modules:
        raise KeyError(f"Module '{logical_name}' not found in catalog")
    entry = modules[logical_name]
    host = catalog.get("registry_host", "app.terraform.io")
    org = catalog.get("organization", "<org>")
    return f"{host}/{org}/{entry['tfe_name']}/{entry['tfe_provider']}"


def local_source(
    catalog: dict[str, Any],
    logical_name: str,
    from_path: Path,
    *,
    root: Path | None = None,
) -> str:
    """Return a relative local source path from from_path to the module."""
    root = (root or repo_root_from(from_path)).resolve()
    entry = catalog["modules"][logical_name]
    target = (root / entry["local_path"]).resolve()
    return os_relpath(from_path.resolve(), target)


def os_relpath(start: Path, target: Path) -> str:
    import os

    return os.path.relpath(target, start).replace("\\", "/")


def list_modules(catalog: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    catalog = catalog or load_catalog()
    rows: list[dict[str, Any]] = []
    for name, entry in sorted(catalog["modules"].items()):
        rows.append(
            {
                "name": name,
                "description": entry.get("description", ""),
                "local_path": entry.get("local_path", ""),
                "tfe_source": tfe_source(catalog, name),
                "version": entry.get("version", ""),
                "depends_on": entry.get("depends_on", []),
            }
        )
    return rows


def resolve_refs(
    catalog: dict[str, Any],
    refs: list[str],
    *,
    use_tfe: bool = False,
    from_path: Path | None = None,
    root: Path | None = None,
) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    from_path = from_path or Path.cwd()
    root = root or repo_root_from(from_path)
    for ref in refs:
        if ref not in catalog["modules"]:
            # Still emit a stub so scaffolds document the intended dependency
            resolved.append(
                {
                    "logical_name": ref,
                    "module_label": ref.split("/")[-1].replace("-", "_"),
                    "source": f"app.terraform.io/<org>/{ref.split('/')[-1]}/{ref.split('/')[0]}"
                    if use_tfe
                    else f"../../{ref}",
                    "version": "~> 1.0" if use_tfe else None,
                    "known": False,
                }
            )
            continue
        entry = catalog["modules"][ref]
        source = (
            tfe_source(catalog, ref)
            if use_tfe
            else local_source(catalog, ref, from_path, root=root)
        )
        resolved.append(
            {
                "logical_name": ref,
                "module_label": entry.get("tfe_name", ref.split("/")[-1]).replace("-", "_"),
                "source": source,
                "version": entry.get("version") if use_tfe else None,
                "known": True,
                "depends_on": entry.get("depends_on", []),
            }
        )
    return resolved
