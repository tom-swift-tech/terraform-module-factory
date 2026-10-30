"""Load require/deny / tag rules from the policy pack for generators and tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tf_factory.policy import load_policies


def required_tags(policies_dir: Path) -> list[str]:
    tags: list[str] = []
    for policy in load_policies(policies_dir).get("TagsRequired", []):
        tags = list(policy.get("required_tags") or tags)
    return tags or ["Environment", "Owner", "CostCenter", "DataClassification"]


def tag_value_patterns(policies_dir: Path) -> dict[str, str]:
    patterns: dict[str, str] = {}
    for policy in load_policies(policies_dir).get("TagsRequired", []):
        patterns.update(policy.get("tag_value_patterns") or {})
    return patterns


def security_rules(policies_dir: Path, cloud: str = "azure") -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    for kind in ("SecurityBaseline", "NetworkingPrivate"):
        for policy in load_policies(policies_dir).get(kind, []):
            if policy.get("cloud") not in {cloud, "multi", None}:
                continue
            for rule in policy.get("rules") or []:
                enriched = dict(rule)
                enriched["_kind"] = kind
                enriched["_policy"] = policy.get("metadata", {}).get("name", kind)
                rules.append(enriched)
    return rules


def attribute_requirements(policies_dir: Path, cloud: str = "azure") -> list[dict[str, Any]]:
    """Flatten require/deny attribute rules for OPA data and tests."""
    out: list[dict[str, Any]] = []
    for rule in security_rules(policies_dir, cloud):
        resource_types = rule.get("resource_types") or []
        require = rule.get("require") or {}
        deny = rule.get("deny") or {}
        for rtype in resource_types:
            for attr, value in require.items():
                out.append(
                    {
                        "id": rule["id"],
                        "resource_type": rtype,
                        "attribute": attr,
                        "op": "eq",
                        "value": value,
                        "severity": rule.get("severity", "error"),
                    }
                )
            for attr, value in deny.items():
                out.append(
                    {
                        "id": rule["id"],
                        "resource_type": rtype,
                        "attribute": attr,
                        "op": "deny_eq",
                        "value": value,
                        "severity": rule.get("severity", "error"),
                    }
                )
    return out
