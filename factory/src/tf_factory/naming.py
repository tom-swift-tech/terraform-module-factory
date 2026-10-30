"""Apply NamingStandard policy rules to render resource names."""

from __future__ import annotations

import re
from typing import Any


def _region_code(policy: dict[str, Any], region: str) -> str:
    regions = policy.get("regions") or {}
    return regions.get(region, region)


def _sanitize(value: str, charset: str | None, lowercase: bool, no_hyphens: bool) -> str:
    result = value.lower() if lowercase else value
    if no_hyphens:
        result = result.replace("-", "").replace("_", "")
    if charset:
        # charset is a character class like [a-z0-9]
        allowed = charset.strip()
        if allowed.startswith("[") and allowed.endswith("]"):
            pattern = allowed
        else:
            pattern = f"[{re.escape(allowed)}]"
        result = "".join(ch for ch in result if re.fullmatch(pattern, ch))
    return result


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

    region_code = _region_code(policy, region)
    pattern = policy.get("pattern", "{prefix}-{workload}-{env}-{region}-{suffix}")

    if no_hyphens:
        # Azure storage accounts: concatenate without separators
        raw = f"{prefix}{workload}{env}{region_code}{suffix}"
    else:
        raw = pattern.format(
            prefix=prefix,
            workload=workload,
            env=env,
            region=region_code,
            suffix=suffix,
        )

    name = _sanitize(raw, charset, lowercase=lowercase, no_hyphens=False if not no_hyphens else True)
    if no_hyphens:
        name = name.replace("-", "")

    max_length = constraints.get("max_length")
    if max_length and len(name) > max_length:
        # Prefer keeping prefix + env + region + suffix; trim workload
        if no_hyphens:
            fixed = f"{prefix}{env}{region_code}{suffix}"
            budget = max_length - len(fixed)
            trimmed_workload = _sanitize(
                workload, charset, lowercase=True, no_hyphens=True
            )[: max(budget, 0)]
            name = f"{prefix}{trimmed_workload}{env}{region_code}{suffix}"[:max_length]
        else:
            name = name[:max_length]

    min_length = constraints.get("min_length")
    if min_length and len(name) < min_length:
        raise ValueError(
            f"Rendered name '{name}' is shorter than min_length={min_length} for {resource_type}"
        )

    return name
