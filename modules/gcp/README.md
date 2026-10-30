# GCP modules

GCP resource modules are not included in v1.

Use the same factory workflow when ready:

1. Add GCP rules to `policies/` (`cloud: gcp` or `multi`).
2. Copy `factory/templates/azure/module` to `factory/templates/gcp/module` and adjust providers.
3. Run `tf-factory scaffold --cloud gcp --name <module> --from-policy policies/`.
4. Register the module in `factory/catalog.yaml`.

Prefer Private Google Access / Private Service Connect patterns analogous to Azure Private Link when authoring baselines.
