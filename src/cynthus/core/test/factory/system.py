"""System factories for the Cynthus project"""

import factory

from ...system import BillingAccount, System, Tenant, TenantType, Workspace
from .user import UserFactory


class SystemFactory(factory.Factory):
    class Meta:
        model = System


class BillingAccountFactory(factory.Factory):
    class Meta:
        model = BillingAccount

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f'Billing account {n}')


class TenantFactory(factory.Factory):
    """A stand-alone personal tenant; pass ``parent=`` for one that belongs to a bridge tenant"""

    class Meta:
        model = Tenant

    name = factory.Sequence(lambda n: f'T{n:05d}')
    type = TenantType.PERSONAL
    owner = factory.SubFactory(UserFactory)


class BridgeTenantFactory(TenantFactory):
    """A parent tenant: same owner as its children, no workspaces"""

    class Meta:
        model = Tenant

    type = TenantType.ORGANIZATIONAL
    bridge = True


class ChildTenantFactory(TenantFactory):
    """A tenant under a bridge tenant with the same owner"""

    class Meta:
        model = Tenant

    parent = factory.SubFactory(BridgeTenantFactory, owner=factory.SelfAttribute('..owner'))


class WorkspaceFactory(factory.Factory):
    class Meta:
        model = Workspace

    name = factory.Sequence(lambda n: f'W{n:05d}')
    tenant = factory.SubFactory(TenantFactory)
    owner = factory.SelfAttribute('tenant.owner')
