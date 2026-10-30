"""Assert Python render_name matches generated Terraform naming module expectations."""

from __future__ import annotations

import json
from pathlib import Path

from tf_factory.generate_naming import generate_naming_module
from tf_factory.naming import fixture_cases, render_name
from tf_factory.policy import load_policy_file


ROOT = Path(__file__).resolve().parents[2]
POLICIES = ROOT / "policies"
NAMING = ROOT / "modules" / "azure" / "naming"


def test_generate_naming_writes_expected_json(tmp_path: Path) -> None:
    out = generate_naming_module(POLICIES, output_dir=tmp_path / "naming")
    expected_path = out / "expected_names.json"
    assert expected_path.is_file()
    data = json.loads(expected_path.read_text(encoding="utf-8"))
    policy = load_policy_file(POLICIES / "naming.example.yaml")
    assert len(data) == len(fixture_cases(policy))
    for row in data:
        got = render_name(
            policy,
            row["resource_type"],
            workload=row["workload"],
            env=row["env"],
            region=row["region"],
            suffix=row["suffix"],
        )
        assert got == row["expected"]


def test_checked_in_naming_module_matches_python() -> None:
    """Regenerate must have been run; expected_names.json agrees with Python."""
    expected_path = NAMING / "expected_names.json"
    assert expected_path.is_file(), "run: tf-factory generate-naming --policies ./policies"
    policy = load_policy_file(POLICIES / "naming.example.yaml")
    data = json.loads(expected_path.read_text(encoding="utf-8"))
    for row in data:
        got = render_name(
            policy,
            row["resource_type"],
            workload=row["workload"],
            env=row["env"],
            region=row["region"],
            suffix=row["suffix"],
        )
        assert got == row["expected"], row
