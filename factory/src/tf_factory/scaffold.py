"""Render Terraform module scaffolds from Jinja2 templates + policy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from tf_factory.catalog import load_catalog, resolve_refs
from tf_factory.policy import naming_policy, repo_root_from, required_module_refs


def templates_dir(root: Path | None = None) -> Path:
    root = root or repo_root_from()
    return root / "factory" / "templates"


def _env(cloud: str) -> Environment:
    loader = FileSystemLoader(str(templates_dir() / cloud / "module"))
    return Environment(
        loader=loader,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )


def scaffold_module(
    *,
    cloud: str,
    name: str,
    policies_dir: Path,
    output_root: Path | None = None,
    use_tfe: bool = False,
    force: bool = False,
) -> Path:
    root = repo_root_from(policies_dir)
    output_root = output_root or (root / "modules" / cloud)
    module_dir = output_root / name

    if module_dir.exists() and any(module_dir.iterdir()) and not force:
        raise FileExistsError(
            f"Module directory already exists and is not empty: {module_dir} "
            "(pass force=True to overwrite)"
        )
    module_dir.mkdir(parents=True, exist_ok=True)

    catalog = load_catalog(root / "factory" / "catalog.yaml")
    refs = required_module_refs(policies_dir, cloud, name.replace("-", "_"))
    # Do not self-reference
    refs = [r for r in refs if not r.endswith(f"/{name}")]
    dependencies = resolve_refs(
        catalog,
        refs,
        use_tfe=use_tfe,
        from_path=module_dir,
        root=root,
    )

    try:
        naming = naming_policy(policies_dir)
    except FileNotFoundError:
        naming = {}

    required_tags = []
    for tag_policy_kind in ("TagsRequired",):
        from tf_factory.policy import load_policies

        for policy in load_policies(policies_dir).get(tag_policy_kind, []):
            required_tags = policy.get("required_tags", required_tags)

    context: dict[str, Any] = {
        "cloud": cloud,
        "module_name": name,
        "module_label": name.replace("-", "_"),
        "dependencies": dependencies,
        "required_tags": required_tags or ["Environment", "Owner", "CostCenter", "DataClassification"],
        "naming_prefixes": (naming.get("resource_prefixes") or {}),
        "private_by_default": True,
        "provider_block": {
            "azure": 'azurerm = {\n    source  = "hashicorp/azurerm"\n    version = "~> 3.100"\n  }',
            "aws": 'aws = {\n    source  = "hashicorp/aws"\n    version = "~> 5.0"\n  }',
            "gcp": 'google = {\n    source  = "hashicorp/google"\n    version = "~> 5.0"\n  }',
        }.get(cloud, ""),
    }

    env = _env(cloud)
    for template_name in env.list_templates():
        template = env.get_template(template_name)
        rendered = template.render(**context)
        # Strip .j2 suffix when present
        out_name = template_name[:-3] if template_name.endswith(".j2") else template_name
        out_path = module_dir / out_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")

    return module_dir
