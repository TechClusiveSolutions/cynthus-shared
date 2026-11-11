"""System fixtures for the Cynthus project"""

from pytest import fixture

from ...system import (
    BillingAccount,
    System,
    Tenant,
    Workspace,
)
from ..factory import (
    BillingAccountFactory,
    BridgeTenantFactory,
    ChildTenantFactory,
    SystemFactory,
    TenantFactory,
    WorkspaceFactory,
)


@fixture
def system() -> System:
    return SystemFactory()


@fixture
def billing_account() -> BillingAccount:
    return BillingAccountFactory()


@fixture
def tenant() -> Tenant:
    return TenantFactory()


@fixture
def bridge_tenant() -> Tenant:
    return BridgeTenantFactory()


@fixture
def child_tenant() -> Tenant:
    return ChildTenantFactory()


@fixture
def workspace() -> Workspace:
    return WorkspaceFactory()
