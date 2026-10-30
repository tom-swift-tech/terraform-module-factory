"""Unit tests for naming policy rendering."""

from pathlib import Path

import pytest

from tf_factory.naming import fixture_cases, render_name
from tf_factory.policy import load_policy_file, validate_policies_dir


ROOT = Path(__file__).resolve().parents[2]
POLICIES = ROOT / "policies"


@pytest.fixture
def policy():
    return load_policy_file(POLICIES / "naming.example.yaml")


def test_policies_validate() -> None:
    results = validate_policies_dir(POLICIES, POLICIES / "schema" / "policy.schema.json")
    assert results
    assert all(not errs for errs in results.values())


def test_storage_account_name(policy) -> None:
    name = render_name(
        policy,
        "storage_account",
        workload="payments",
        env="prod",
        region="eastus",
        suffix="01",
    )
    assert name == "stpaymentsprodeus01"
    assert name.isalnum()
    assert name.islower()
    assert len(name) <= 24
    assert name.endswith("01")


def test_key_vault_preserves_suffix_when_truncated(policy) -> None:
    a = render_name(
        policy,
        "key_vault",
        workload="claimsprocessing",
        env="prod",
        region="eastus2",
        suffix="01",
    )
    b = render_name(
        policy,
        "key_vault",
        workload="claimsprocessing",
        env="prod",
        region="eastus2",
        suffix="02",
    )
    assert a != b
    assert a.endswith("-01")
    assert b.endswith("-02")
    assert not a.endswith("-")
    assert len(a) <= 24
    assert len(b) <= 24


def test_storage_truncates_workload_not_suffix(policy) -> None:
    name = render_name(
        policy,
        "storage_account",
        workload="claimsprocessingsvc",
        env="staging",
        region="eastus",
        suffix="01",
    )
    assert name.endswith("01")
    assert "staging" in name
    assert len(name) <= 24


def test_fixture_cases_all_render(policy) -> None:
    for case in fixture_cases(policy):
        name = render_name(
            policy,
            case["resource_type"],
            workload=case["workload"],
            env=case["env"],
            region=case["region"],
            suffix=case["suffix"],
        )
        assert name
        assert not name.startswith("-")
        assert not name.endswith("-")
