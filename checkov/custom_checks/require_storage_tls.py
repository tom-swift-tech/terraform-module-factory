"""CKV2_TFFACTORY_AZURE_2: Require TLS 1.2+ on storage accounts."""

from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RequireStorageTls(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure storage accounts enforce TLS 1.2 or higher"
        id = "CKV2_TFFACTORY_AZURE_2"
        supported_resources = ("azurerm_storage_account",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        value = conf.get("min_tls_version")
        if value is None:
            return CheckResult.FAILED
        tls = value[0] if isinstance(value, list) else value
        if tls in ("TLS1_2", "TLS1_3"):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = RequireStorageTls()
