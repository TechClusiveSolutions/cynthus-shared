"""Tenant, parent tenant, workspace and billing account unit tests for the Cynthus project (ADR-010)"""

import pytest
from pydantic import ValidationError

from cynthus.core.system import BillingAccount, System, Tenant, Workspace
from cynthus.core.user import User


@pytest.fixture
def owner():
    return User(first_name='John', last_name='Doe', email='John.Doe@example.com')


@pytest.fixture
def other():
    return User(first_name='Jane', last_name='Roe', email='Jane.Roe@example.com')


def bridge(owner):
    return Tenant(name='T00003', type='organizational', owner=owner, bridge=True)


def test_a_tenant_can_stand_alone(owner):
    tenant = Tenant(name='T00001', type='personal', owner=owner)

    assert tenant.parent is None
    assert tenant.bridge is False
    assert tenant.billing_account_id is None


def test_the_owner_s_tenants_share_a_parent_with_the_same_owner(owner):
    parent = bridge(owner)
    first = Tenant(name='T00001', type='personal', owner=owner, parent=parent)
    second = Tenant(name='T00002', type='organizational', owner=owner, parent=parent)

    assert first.parent is second.parent or first.parent == second.parent
    assert first.parent.owner == second.owner == owner


def test_a_parent_must_be_a_bridge(owner):
    not_a_bridge = Tenant(name='T00009', type='personal', owner=owner)

    with pytest.raises(ValidationError, match='must be a bridge tenant'):
        Tenant(name='T00001', type='personal', owner=owner, parent=not_a_bridge)


def test_a_parent_has_the_same_owner_as_its_children(owner, other):
    with pytest.raises(ValidationError, match='same owner'):
        Tenant(name='T00001', type='personal', owner=other, parent=bridge(owner))


def test_a_parent_has_no_parent_of_its_own(owner):
    with pytest.raises(ValidationError, match='cannot have a parent of its own'):
        Tenant(name='T00004', type='organizational', owner=owner, bridge=True, parent=bridge(owner))


def test_a_workspace_belongs_to_a_working_tenant(owner):
    tenant = Tenant(name='T00001', type='personal', owner=owner)

    assert Workspace(name='W00001', tenant=tenant, owner=owner).tenant is tenant


def test_a_parent_tenant_has_no_workspaces(owner):
    with pytest.raises(ValidationError, match='has no workspaces'):
        Workspace(name='W00001', tenant=bridge(owner), owner=owner)


def test_billing_accounts_are_chosen_per_tenant(owner):
    parent = bridge(owner)
    first = Tenant(name='T00001', type='personal', owner=owner, parent=parent)
    second = Tenant(name='T00002', type='organizational', owner=owner, parent=parent)
    shared = BillingAccount(owner=owner, name='Main', options={'invoice': 'monthly'})
    separate = BillingAccount(owner=owner, name='Business')

    first.attach_billing_account(shared)
    second.attach_billing_account(separate)
    parent.attach_billing_account(shared)

    assert first.billing_account_id == parent.billing_account_id == shared.id_
    assert second.billing_account_id == separate.id_
    assert shared.options == {'invoice': 'monthly'}
    assert separate.options == {}


def test_each_billing_account_keeps_its_own_options(owner):
    first = BillingAccount(owner=owner, name='A')
    second = BillingAccount(owner=owner, name='B')

    first.options['invoice'] = 'yearly'

    assert second.options == {}


def test_a_tenant_cannot_be_billed_to_another_owner_s_account(owner, other):
    tenant = Tenant(name='T00001', type='personal', owner=owner)

    with pytest.raises(ValueError, match='account of its owner'):
        tenant.attach_billing_account(BillingAccount(owner=other, name='Theirs'))

    assert tenant.billing_account_id is None


def test_the_system_has_a_fixed_identity():
    system = System()

    assert system.id_ == System().id_
    assert system.name == 'Cynthus Life'
