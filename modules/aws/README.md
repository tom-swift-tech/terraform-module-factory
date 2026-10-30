# AWS modules

AWS resource modules are not included in v1.

Use the same factory workflow when ready:

1. Add AWS rules to `policies/` (`cloud: aws` or `multi`).
2. Copy `factory/templates/azure/module` to `factory/templates/aws/module` and adjust providers.
3. Run `tf-factory scaffold --cloud aws --name <module> --from-policy policies/`.
4. Register the module in `factory/catalog.yaml`.

Shared policy concepts (private connectivity, naming, required tags) apply across clouds; encode provider-specific rule bodies under each policy file.
