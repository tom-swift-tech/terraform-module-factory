"""tf-factory CLI entrypoint."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from tf_factory import __version__
from tf_factory.catalog import list_modules, load_catalog
from tf_factory.naming import render_name
from tf_factory.policy import naming_policy, repo_root_from, validate_policies_dir
from tf_factory.scaffold import scaffold_module

app = typer.Typer(
    name="tf-factory",
    help="Scaffold and validate Terraform modules against platform policy packs.",
    no_args_is_help=True,
)
console = Console()


def _policies_dir(policies: Optional[Path]) -> Path:
    if policies:
        return policies.resolve()
    root = repo_root_from()
    return (root / "policies").resolve()


@app.callback()
def main_callback() -> None:
    """Terraform module factory."""


@app.command("version")
def version_cmd() -> None:
    """Print CLI version."""
    console.print(__version__)


@app.command("validate-policy")
def validate_policy_cmd(
    policies: Optional[Path] = typer.Option(
        None,
        "--policies",
        help="Path to policies directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
) -> None:
    """Schema-validate all YAML/JSON policy files."""
    policies_dir = _policies_dir(policies)
    schema_path = policies_dir / "schema" / "policy.schema.json"
    results = validate_policies_dir(policies_dir, schema_path if schema_path.exists() else None)

    failures = 0
    for path, errors in results.items():
        if errors:
            failures += 1
            console.print(f"[red]FAIL[/red] {path}")
            for err in errors:
                console.print(f"  - {err}")
        else:
            console.print(f"[green]OK[/green]   {path}")

    if not results:
        console.print("[yellow]No policy files found.[/yellow]")
        raise typer.Exit(code=1)

    if failures:
        console.print(f"\n[red]{failures} policy file(s) failed validation.[/red]")
        raise typer.Exit(code=1)

    console.print(f"\n[green]Validated {len(results)} policy file(s).[/green]")


@app.command("list-modules")
def list_modules_cmd(
    catalog: Optional[Path] = typer.Option(
        None,
        "--catalog",
        help="Path to catalog.yaml",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
) -> None:
    """List modules from the factory catalog."""
    data = load_catalog(catalog) if catalog else load_catalog()
    rows = list_modules(data)
    table = Table(title="Module catalog")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Local path")
    table.add_column("TFE source")
    table.add_column("Version")
    for row in rows:
        table.add_row(
            row["name"],
            row["description"],
            row["local_path"],
            row["tfe_source"],
            row["version"],
        )
    console.print(table)


@app.command("render-name")
def render_name_cmd(
    resource_type: str = typer.Option(..., "--type", help="Resource type key from naming policy"),
    workload: str = typer.Option(..., "--workload"),
    env: str = typer.Option(..., "--env"),
    region: str = typer.Option(..., "--region"),
    suffix: str = typer.Option("01", "--suffix"),
    policies: Optional[Path] = typer.Option(
        None,
        "--policies",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
) -> None:
    """Dry-run a resource name from the NamingStandard policy."""
    policies_dir = _policies_dir(policies)
    policy = naming_policy(policies_dir)
    name = render_name(
        policy,
        resource_type,
        workload=workload,
        env=env,
        region=region,
        suffix=suffix,
    )
    console.print(name)


@app.command("scaffold")
def scaffold_cmd(
    cloud: str = typer.Option("azure", "--cloud", help="Target cloud: azure|aws|gcp"),
    name: str = typer.Option(..., "--name", help="Module directory name"),
    from_policy: Optional[Path] = typer.Option(
        None,
        "--from-policy",
        help="Policies directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Output parent directory (defaults to modules/<cloud>)",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    use_tfe: bool = typer.Option(False, "--use-tfe", help="Emit TFE registry sources"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing module files"),
) -> None:
    """Scaffold a new Terraform module with secure defaults and catalog refs."""
    if cloud not in {"azure", "aws", "gcp"}:
        console.print("[red]cloud must be azure, aws, or gcp[/red]")
        raise typer.Exit(code=1)

    policies_dir = _policies_dir(from_policy)
    if cloud != "azure":
        # Templates currently ship for azure; create cloud template dir message
        template_root = repo_root_from(policies_dir) / "factory" / "templates" / cloud / "module"
        if not template_root.is_dir():
            console.print(
                f"[red]No templates for cloud '{cloud}' at {template_root}. "
                "Copy factory/templates/azure/module as a starting point.[/red]"
            )
            raise typer.Exit(code=1)

    try:
        module_dir = scaffold_module(
            cloud=cloud,
            name=name,
            policies_dir=policies_dir,
            output_root=output,
            use_tfe=use_tfe,
            force=force,
        )
    except FileExistsError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Scaffolded[/green] {module_dir}")


if __name__ == "__main__":
    app()
