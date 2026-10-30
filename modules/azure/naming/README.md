# azure/naming

**Generated** from the NamingStandard policy by `tf-factory generate-naming`.

Do not edit `main.tf` / `variables.tf` / `outputs.tf` by hand. Change the policy, then regenerate:

```bash
tf-factory generate-naming --policies ./policies
```

## Truncation rules

- Preserves **prefix**, **environment**, **region**, and **suffix**
- Shortens only the **workload** segment
- Never leaves a leading/trailing `-`
- Different suffixes must not collide when fixed segments fit in `max_length`

## Parity

`expected_names.json` is written from the same Python `render_name` used by `tf-factory render-name`.
`terraform test` and `factory/tests/test_naming_parity.py` assert Python and Terraform agree.
