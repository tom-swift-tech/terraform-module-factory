"""Scaffold and catalog tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

from tf_factory.catalog import list_modules, load_catalog, tfe_source
from tf_factory.scaffold import scaffold_module


ROOT = Path(__file__).resolve().parents[2]
POLICIES = ROOT / "policies"


def test_catalog_uses_azurerm_provider_and_version_fields() -> None:
    catalog = load_catalog(ROOT / "factory" / "catalog.yaml")
    rows = list_modules(catalog)
    assert rows
    for row in rows:
        assert row["tfe_source"].endswith("/azurerm")
        assert row["version"]
        assert row["version_constraint"].startswith("~>")
        assert "source_directory" in row
        src = tfe_source(catalog, row["name"])
        assert "/azurerm" in src


def test_scaffold_wires_required_inputs_and_validates(tmp_path: Path) -> None:
    module_dir = scaffold_module(
        cloud="azure",
        name="cache",
        policies_dir=POLICIES,
        output_root=tmp_path,
        force=True,
    )
    main = (module_dir / "main.tf").read_text(encoding="utf-8")
    assert 'module "naming"' in main
    assert "workload" in main
    assert 'module "private_endpoint"' in main
    assert "subnet_id" in main

    # Relative sources point at the real repo modules for validate
    # Rewrite sources to workspace modules for terraform validate
    catalog = load_catalog(ROOT / "factory" / "catalog.yaml")
    naming_src = (ROOT / catalog["modules"]["azure/naming"]["local_path"]).resolve()
    pe_src = (ROOT / catalog["modules"]["azure/private-endpoint"]["local_path"]).resolve()
    main = main.replace(
        # generated relative paths from tmp may be deep; force absolute-style via symlink
        main,
        main,
    )
    # Create local symlinks so relative ../ paths from a flat tmp module work
    # Instead: rewrite source lines to absolute paths (Terraform accepts them)
    import re

    def repl_naming(match: re.Match[str]) -> str:
        return f'source = "{naming_src}"'

    def repl_pe(match: re.Match[str]) -> str:
        return f'source = "{pe_src}"'

    main2 = re.sub(r'source\s*=\s*"[^"]*naming[^"]*"', repl_naming, main, count=1)
    main2 = re.sub(r'source\s*=\s*"[^"]*private-endpoint[^"]*"', repl_pe, main2, count=1)
    (module_dir / "main.tf").write_text(main2, encoding="utf-8")

    subprocess.run(
        ["terraform", "init", "-backend=false", "-input=false"],
        cwd=module_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    proc = subprocess.run(
        ["terraform", "validate", "-no-color"],
        cwd=module_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
