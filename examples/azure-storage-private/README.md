# Example: private Azure storage

Composes `azure/naming` and `azure/storage` (which embeds `azure/private-endpoint`).

## Local validate

```bash
cd examples/azure-storage-private
terraform init -backend=false
terraform validate
```

## Apply (real subscription)

Override the placeholder subnet and DNS zone ids:

```bash
terraform plan \
  -var resource_group_name=rg-myapp-dev \
  -var private_endpoint_subnet_id=/subscriptions/.../subnets/snet-pe \
  -var blob_private_dns_zone_id=/subscriptions/.../privateDnsZones/privatelink.blob.core.windows.net
```
