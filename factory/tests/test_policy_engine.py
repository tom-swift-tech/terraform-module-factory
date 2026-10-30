"""Policy pack rule export tests."""

from pathlib import Path

from tf_factory.policy_engine import attribute_requirements, required_tags, tag_value_patterns


POLICIES = Path(__file__).resolve().parents[2] / "policies"


def test_required_tags_from_policy() -> None:
    tags = required_tags(POLICIES)
    assert "Environment" in tags
    assert "DataClassification" in tags


def test_tag_value_patterns_exported() -> None:
    patterns = tag_value_patterns(POLICIES)
    assert "Environment" in patterns
    assert "DataClassification" in patterns


def test_attribute_requirements_include_public_deny() -> None:
    rules = attribute_requirements(POLICIES, "azure")
    ids = {r["id"] for r in rules}
    assert "deny-public-network-access" in ids or "deny-public-acl-as-primary" in ids
    assert any(r["attribute"] == "public_network_access_enabled" for r in rules)
