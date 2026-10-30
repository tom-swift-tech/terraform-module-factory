"""Load and validate YAML/JSON policy packs against the factory schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

POLICY_KINDS = {
    "NamingStandard",
    "SecurityBaseline",
    "NetworkingPrivate",
    "TagsRequired",
}


def repo_root_from(start: Path | None = None) -> Path:
    """Walk upward until policies/ and factory/ are found."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "policies").is_dir() and (candidate / "factory").is_dir():
            return candidate
    return current


def default_schema_path(root: Path | None = None) -> Path:
    root = root or repo_root_from()
    return root / "policies" / "schema" / "policy.schema.json"


def load_schema(schema_path: Path | None = None) -> dict[str, Any]:
    path = schema_path or default_schema_path()
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_policy_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    elif path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        raise ValueError(f"Unsupported policy file type: {path}")
    if not isinstance(data, dict):
        raise ValueError(f"Policy file must be a mapping: {path}")
    return data


def iter_policy_files(policies_dir: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("*.yaml", "*.yml", "*.json"):
        files.extend(policies_dir.glob(pattern))
    return sorted(p for p in files if p.is_file())


def validate_policy(data: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or load_schema()
    validator = Draft202012Validator(schema)
    return [
        f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}"
        for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    ]


def validate_policies_dir(policies_dir: Path, schema_path: Path | None = None) -> dict[str, list[str]]:
    schema = load_schema(schema_path)
    results: dict[str, list[str]] = {}
    for path in iter_policy_files(policies_dir):
        try:
            data = load_policy_file(path)
            errors = validate_policy(data, schema)
        except Exception as exc:  # noqa: BLE001 - surface file-level failures to CLI
            errors = [str(exc)]
        results[str(path)] = errors
    return results


def load_policies(policies_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Return policies grouped by kind."""
    grouped: dict[str, list[dict[str, Any]]] = {kind: [] for kind in POLICY_KINDS}
    for path in iter_policy_files(policies_dir):
        data = load_policy_file(path)
        kind = data.get("kind")
        if kind in grouped:
            data["_source"] = str(path)
            grouped[kind].append(data)
    return grouped


def naming_policy(policies_dir: Path) -> dict[str, Any]:
    naming = load_policies(policies_dir).get("NamingStandard") or []
    if not naming:
        raise FileNotFoundError(f"No NamingStandard policy found under {policies_dir}")
    return naming[0]


def required_module_refs(policies_dir: Path, cloud: str, module_name: str) -> list[str]:
    """Collect module references required by networking/security policies."""
    refs: list[str] = []
    for kind in ("SecurityBaseline", "NetworkingPrivate"):
        for policy in load_policies(policies_dir).get(kind, []):
            if policy.get("cloud") not in {cloud, "multi", None}:
                continue
            for ref in policy.get("required_module_refs", []):
                if ref not in refs:
                    refs.append(ref)
            for rule in policy.get("rules", []):
                when = rule.get("when") or []
                must = rule.get("must_reference_module")
                if must and (not when or module_name in when or module_name.replace("-", "_") in when):
                    if must not in refs:
                        refs.append(must)
    # Always include naming for azure scaffolds when present in catalog policies
    if cloud == "azure" and "azure/naming" not in refs:
        refs.insert(0, "azure/naming")
    return refs
