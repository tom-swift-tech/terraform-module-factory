"""CKV2_TFFACTORY_AZURE_3: Deny public nested blob access."""

from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DenyPublicBlobAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure storage accounts disallow public nested items"
        id = "CKV2_TFFACTORY_AZURE_3"
        supported_resources = ("azurerm_storage_account",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        value = conf.get("allow_nested_items_to_be_public")
        if value is None:
            return CheckResult.FAILED
        allowed = value[0] if isinstance(value, list) else value
        if allowed is True or allowed == "true":
            return CheckResult.FAILED
        return CheckResult.PASSED


check = DenyPublicBlobAccess()
