# tf-factory

Python CLI that scaffolds Terraform modules aligned to platform policy packs.

## Install

```bash
cd factory
pip install -e .
```

## Commands

```bash
tf-factory validate-policy --policies ../policies
tf-factory list-modules
tf-factory render-name --type storage_account --workload app --env prod --region eastus --suffix 01
tf-factory scaffold --cloud azure --name redis --from-policy ../policies
```

See the repository root README for full workflow documentation.
