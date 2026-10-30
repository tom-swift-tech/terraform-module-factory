"""Unit tests for naming policy rendering."""

from pathlib import Path

from tf_factory.naming import render_name
from tf_factory.policy import load_policy_file, validate_policies_dir


ROOT = Path(__file__).resolve().parents[2]
POLICIES = ROOT / "policies"


def test_policies_validate() -> None:
    results = validate_policies_dir(POLICIES, POLICIES / "schema" / "policy.schema.json")
    assert results
    assert all(not errs for errs in results.values())


def test_storage_account_name() -> None:
    policy = load_policy_file(POLICIES / "naming.example.yaml")
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


def test_key_vault_name() -> None:
    policy = load_policy_file(POLICIES / "naming.example.yaml")
    name = render_name(
        policy,
        "key_vault",
        workload="payments",
        env="prod",
        region="eastus",
        suffix="01",
    )
    assert name.startswith("kv-")
    assert len(name) <= 24
