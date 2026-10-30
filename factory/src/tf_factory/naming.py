"""Apply NamingStandard policy rules to render resource names.

Truncation always preserves prefix, environment, region, and suffix.
Only the workload segment is shortened. Results never end with a hyphen.
Different suffixes must not collide when the fixed segments fit in max_length.
"""

from __future__ import annotations

import re
from typing import Any


def _region_code(policy: dict[str, Any], region: str) -> str:
    regions = policy.get("regions") or {}
    if region in regions:
        return regions[region]
    return re.sub(r"[^a-z0-9]", "", region.lower())


def _sanitize_segment(
    value: str,
    charset: str | None,
    *,
    lowercase: bool,
    no_hyphens: bool,
) -> str:
    result = value.lower() if lowercase else value
    if no_hyphens:
        result = result.replace("-", "").replace("_", "")
    if charset:
        allowed = charset.strip()
        pattern = allowed if allowed.startswith("[") and allowed.endswith("]") else f"[{re.escape(allowed)}]"
        result = "".join(ch for ch in result if re.fullmatch(pattern, ch))
    return result


def _strip_edge_hyphens(value: str) -> str:
    return value.strip("-")


def _join_hyphenated(parts: list[str]) -> str:
    return "-".join(p for p in parts if p)


def render_name(
    policy: dict[str, Any],
    resource_type: str,
    *,
    workload: str,
    env: str,
    region: str,
    suffix: str = "01",
) -> str:
    prefixes = policy.get("resource_prefixes") or {}
    if resource_type not in prefixes:
        raise KeyError(
            f"Unknown resource type '{resource_type}'. "
            f"Known: {', '.join(sorted(prefixes))}"
        )

    prefix = prefixes[resource_type]
    constraints = (policy.get("resource_constraints") or {}).get(resource_type, {})
    no_hyphens = bool(constraints.get("no_hyphens", False))
    lowercase = bool(constraints.get("lowercase", True))
    charset = constraints.get("charset")
    max_length = constraints.get("max_length")
    min_length = constraints.get("min_length")

    region_code = _region_code(policy, region)
    workload_clean = _sanitize_segment(
        workload, charset, lowercase=lowercase, no_hyphens=no_hyphens
    )
    prefix_clean = _sanitize_segment(prefix, charset, lowercase=lowercase, no_hyphens=no_hyphens)
    env_clean = _sanitize_segment(env, charset, lowercase=lowercase, no_hyphens=no_hyphens)
    region_clean = _sanitize_segment(
        region_code, charset, lowercase=lowercase, no_hyphens=no_hyphens
    )
    suffix_clean = _sanitize_segment(
        suffix, charset, lowercase=lowercase, no_hyphens=no_hyphens
    )

    if no_hyphens:
        fixed_len = len(prefix_clean) + len(env_clean) + len(region_clean) + len(suffix_clean)
        if max_length is not None and fixed_len > max_length:
            raise ValueError(
                f"Fixed segments for {resource_type} exceed max_length={max_length} "
                f"(need {fixed_len} without workload)"
            )
        budget = (max_length - fixed_len) if max_length is not None else len(workload_clean)
        trimmed_workload = workload_clean[: max(budget, 0)]
        name = f"{prefix_clean}{trimmed_workload}{env_clean}{region_clean}{suffix_clean}"
    else:
        # prefix-workload-env-region-suffix; hyphens between non-empty parts
        separators = 4  # worst case between 5 parts
        fixed_len = (
            len(prefix_clean) + len(env_clean) + len(region_clean) + len(suffix_clean) + separators
        )
        # If workload empty we use fewer separators; budget uses worst-case then re-join
        if max_length is not None and (
            len(prefix_clean) + len(env_clean) + len(region_clean) + len(suffix_clean) + 3
        ) > max_length:
            raise ValueError(
                f"Fixed segments for {resource_type} exceed max_length={max_length} "
                "even with an empty workload"
            )
        if max_length is not None:
            # Recompute overhead with workload present (4 hyphens)
            overhead = (
                len(prefix_clean)
                + len(env_clean)
                + len(region_clean)
                + len(suffix_clean)
                + 4
            )
            budget = max(max_length - overhead, 0)
            trimmed_workload = workload_clean[:budget]
        else:
            trimmed_workload = workload_clean

        name = _join_hyphenated(
            [prefix_clean, trimmed_workload, env_clean, region_clean, suffix_clean]
        )
        name = _strip_edge_hyphens(name)
        # Collapse accidental double hyphens if workload empty
        while "--" in name:
            name = name.replace("--", "-")
        name = _strip_edge_hyphens(name)

        if max_length is not None and len(name) > max_length:
            # Should not happen if budget math is right; final safety without eating suffix
            overhead = len(prefix_clean) + len(env_clean) + len(region_clean) + len(suffix_clean) + 4
            budget = max(max_length - overhead, 0)
            trimmed_workload = workload_clean[:budget]
            name = _strip_edge_hyphens(
                _join_hyphenated(
                    [prefix_clean, trimmed_workload, env_clean, region_clean, suffix_clean]
                )
            )

    if min_length and len(name) < min_length:
        raise ValueError(
            f"Rendered name '{name}' is shorter than min_length={min_length} for {resource_type}"
        )
    if max_length and len(name) > max_length:
        raise ValueError(
            f"Rendered name '{name}' exceeds max_length={max_length} for {resource_type}"
        )
    if name.endswith("-") or name.startswith("-"):
        raise ValueError(f"Rendered name '{name}' has edge hyphens for {resource_type}")

    return name


def fixture_cases(policy: dict[str, Any]) -> list[dict[str, Any]]:
    """Canonical cases used by Python and Terraform parity tests."""
    return [
        {
            "resource_type": "key_vault",
            "workload": "claimsprocessing",
            "env": "prod",
            "region": "eastus2",
            "suffix": "01",
        },
        {
            "resource_type": "key_vault",
            "workload": "claimsprocessing",
            "env": "prod",
            "region": "eastus2",
            "suffix": "02",
        },
        {
            "resource_type": "storage_account",
            "workload": "claimsprocessingsvc",
            "env": "staging",
            "region": "eastus",
            "suffix": "01",
        },
        {
            "resource_type": "storage_account",
            "workload": "payments",
            "env": "prod",
            "region": "eastus",
            "suffix": "01",
        },
        {
            "resource_type": "private_endpoint",
            "workload": "claimsprocessing",
            "env": "prod",
            "region": "eastus2",
            "suffix": "01",
        },
        {
            "resource_type": "key_vault",
            "workload": "app",
            "env": "dev",
            "region": "eastus",
            "suffix": "01",
        },
    ]
