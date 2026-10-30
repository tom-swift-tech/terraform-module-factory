"""Render Terraform module scaffolds from Jinja2 templates + policy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from tf_factory.catalog import load_catalog, resolve_refs
from tf_factory.policy import naming_policy, repo_root_from, required_module_refs
from tf_factory.policy_engine import required_tags as load_required_tags


def templates_dir(root: Path | None = None) -> Path:
    root = root or repo_root_from()
    return root / "factory" / "templates"


def _env(cloud: str, root: Path | None = None) -> Environment:
    loader = FileSystemLoader(str(templates_dir(root) / cloud / "module"))
    return Environment(
        loader=loader,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )


# Variables every Azure scaffold must declare so dependency modules validate.
_BASE_AZURE_VARIABLES: list[dict[str, Any]] = [
    {
        "name": "workload",
        "type": "string",
        "description": "Workload identifier for naming.",
    },
    {
        "name": "environment",
        "type": "string",
        "description": "Environment code (dev|test|staging|prod).",
    },
    {
        "name": "location",
        "type": "string",
        "description": "Azure region.",
    },
    {
        "name": "suffix",
        "type": "string",
        "description": "Naming suffix (preserved under truncation).",
        "default": '"01"',
    },
    {
        "name": "resource_group_name",
        "type": "string",
        "description": "Resource group name.",
    },
    {
        "name": "private_endpoint_subnet_id",
        "type": "string",
        "description": "Subnet id for Private Endpoints.",
        "default": "null",
    },
    {
        "name": "private_endpoint_name",
        "type": "string",
        "description": "Private Endpoint name override.",
        "default": "null",
    },
    {
        "name": "private_connection_resource_id",
        "type": "string",
        "description": "Target resource id for Private Endpoint (set when wiring PE).",
        "default": "null",
    },
    {
        "name": "private_endpoint_subresources",
        "type": "list(string)",
        "description": "Private Link subresource names.",
        "default": '["vault"]',
    },
    {
        "name": "private_dns_zone_ids",
        "type": "list(string)",
        "description": "Private DNS zone ids for PE zone group.",
        "default": "[]",
    },
    {
        "name": "create_private_endpoint",
        "type": "bool",
        "description": "Create composed Private Endpoint (platform default).",
        "default": "true",
    },
    {
        "name": "allow_public_network_access",
        "type": "bool",
        "description": "BREAK-GLASS only. Leave false.",
        "default": "false",
    },
]


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

    tags = load_required_tags(policies_dir)

    context: dict[str, Any] = {
        "cloud": cloud,
        "module_name": name,
        "module_label": name.replace("-", "_"),
        "dependencies": dependencies,
        "required_tags": tags,
        "extra_variables": _BASE_AZURE_VARIABLES if cloud == "azure" else [],
        "naming_prefixes": (naming.get("resource_prefixes") or {}),
        "private_by_default": True,
        "provider_block": {
            "azure": (
                'azurerm = {\n'
                '    source  = "hashicorp/azurerm"\n'
                '    version = "~> 4.0"\n'
                "  }"
            ),
            "aws": 'aws = {\n    source  = "hashicorp/aws"\n    version = "~> 5.0"\n  }',
            "gcp": 'google = {\n    source  = "hashicorp/google"\n    version = "~> 5.0"\n  }',
        }.get(cloud, ""),
    }

    env = _env(cloud, root)
    for template_name in env.list_templates():
        template = env.get_template(template_name)
        rendered = template.render(**context)
        out_name = template_name[:-3] if template_name.endswith(".j2") else template_name
        out_path = module_dir / out_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")

    return module_dir
