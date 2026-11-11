"""The core model fixtures and factories build valid, consistent objects"""

# A fixture is used by naming it as a test argument, which ruff reads as redefining the import
# ruff: noqa: F811

import pytest

from cynthus.core.event import (
    Event,
    EventRequest,
    EventRequestDecision,
    EventRequestResponse,
    InventoryEvent,
    SystemEvent,
    UserEvent,
)
from cynthus.core.resource import Item, ItemBrand, StorageLocation, StorageLocationShelf, StorageShelf, StorageShelfItem
from cynthus.core.service import (
    InventoryService,
    LogisticsService,
    ProfileService,
    RecipeService,
    ShoppingService,
)
from cynthus.core.soft_deletable import SoftDeletable
from cynthus.core.system import BillingAccount, System, Tenant, Workspace
from cynthus.core.test.factory import (
    BridgeTenantFactory,
    ChildTenantFactory,
    EventFactory,
    EventRequestResponseFactory,
    StorageLocationShelfFactory,
    TenantFactory,
    UserEventFactory,
    UserFactory,
    WorkspaceFactory,
)
from cynthus.core.test.fixture import (  # noqa: F401  (a fixture is used by naming it as an argument)
    billing_account,
    bridge_tenant,
    child_tenant,
    event,
    event_request,
    event_request_decision,
    event_request_response,
    inventory_event,
    inventory_service,
    item,
    item_brand,
    logistics_service,
    profile_service,
    recipe_service,
    shopping_service,
    storage_location,
    storage_location_shelf,
    storage_shelf,
    storage_shelf_item,
    system,
    system_event,
    tenant,
    user,
    user_event,
    workspace,
)
from cynthus.core.user import User

BUILT = [
    ('user', User), ('system', System), ('billing_account', BillingAccount), ('tenant', Tenant),
    ('bridge_tenant', Tenant), ('child_tenant', Tenant), ('workspace', Workspace),
    ('inventory_service', InventoryService), ('profile_service', ProfileService),
    ('shopping_service', ShoppingService), ('logistics_service', LogisticsService), ('recipe_service', RecipeService),
    ('item_brand', ItemBrand), ('item', Item), ('storage_location', StorageLocation), ('storage_shelf', StorageShelf),
    ('storage_shelf_item', StorageShelfItem), ('storage_location_shelf', StorageLocationShelf),
    ('event', Event), ('user_event', UserEvent), ('inventory_event', InventoryEvent), ('system_event', SystemEvent),
    ('event_request', EventRequest), ('event_request_decision', EventRequestDecision),
    ('event_request_response', EventRequestResponse),
]


@pytest.mark.parametrize('name, model', BUILT)
def test_every_fixture_builds_its_class(request, name, model):
    assert type(request.getfixturevalue(name)) is model


# An event holds its resource as the base Resource, so JSON drops the fields of the real kind (a location's type, a
# shelf's slots). Those objects do not come back equal; a tagged union on the resource would fix it (ADR-009 follow-up).
POLYMORPHIC = {'event', 'user_event', 'inventory_event', 'system_event', 'event_request', 'event_request_response'}


@pytest.mark.parametrize('name, model', BUILT)
def test_every_fixture_serializes_to_json_that_reads_back_to_the_same_json(request, name, model):
    built = request.getfixturevalue(name)
    dumped = built.model_dump_json()

    assert model.model_validate_json(dumped).model_dump_json() == dumped


@pytest.mark.parametrize('name, model', [entry for entry in BUILT if entry[0] not in POLYMORPHIC])
def test_every_fixture_without_a_polymorphic_part_survives_a_json_round_trip(request, name, model):
    built = request.getfixturevalue(name)

    assert model.model_validate_json(built.model_dump_json()) == built


@pytest.mark.xfail(strict=True, reason='an event holds a Resource, so the fields of its real kind are lost in JSON')
def test_an_event_keeps_the_kind_of_its_resource_through_json(event):
    assert type(Event.model_validate_json(event.model_dump_json()).resource) is type(event.resource)


def test_each_build_is_a_new_object(user):
    assert UserFactory().id_ != UserFactory().id_ != user.id_


def test_a_child_tenant_has_a_bridge_parent_with_the_same_owner(child_tenant):
    assert child_tenant.parent.bridge
    assert child_tenant.parent.owner == child_tenant.owner


def test_a_bridge_tenant_has_no_workspaces():
    bridge = BridgeTenantFactory()

    with pytest.raises(ValueError, match='has no workspaces'):
        WorkspaceFactory(tenant=bridge)


def test_siblings_can_share_one_bridge():
    first = ChildTenantFactory()
    second = ChildTenantFactory(parent=first.parent, owner=first.owner)

    assert first.parent == second.parent


def test_a_workspace_is_owned_by_the_owner_of_its_tenant(workspace):
    assert workspace.owner == workspace.tenant.owner


def test_an_event_is_consistent_through_its_tenant_workspace_and_resource(event):
    assert event.workspace.tenant == event.tenant
    assert event.resource.workspace == event.workspace


def test_a_user_event_is_by_the_owner_of_the_tenant(user_event):
    assert user_event.user == user_event.tenant.owner


def test_a_request_is_made_by_the_user_of_its_event(event_request):
    assert event_request.requestor == event_request.event.user


def test_a_location_shelf_belongs_to_the_workspace_of_its_location():
    placed = StorageLocationShelfFactory()

    assert placed.shelf.workspace == placed.location.workspace


def test_a_response_starts_undecided(event_request_response):
    assert event_request_response.decision is None


def test_factories_take_overrides():
    owner = UserFactory(first_name='Grace')
    tenant = TenantFactory(owner=owner, name='T-grace')
    shared = UserEventFactory(tenant=tenant, data={'a': 1})

    assert shared.tenant.name == 'T-grace' and shared.data == {'a': 1}
    assert EventFactory().data == {}
    assert EventRequestResponseFactory().request.event.tenant != shared.tenant


@pytest.mark.parametrize('name', [
    'user', 'tenant', 'workspace', 'billing_account', 'item', 'storage_location', 'storage_shelf',
    'storage_shelf_item', 'storage_location_shelf',
])
def test_what_holds_a_person_s_data_can_be_soft_deleted(request, name):
    built = request.getfixturevalue(name)

    assert isinstance(built, SoftDeletable)
    assert built.deleted_at is None and not built.is_deleted

    stamp = built.soft_delete()

    assert built.is_deleted and built.deleted_at == stamp
    assert built.model_dump(mode='json')['deleted_at'] is not None

    built.restore()

    assert not built.is_deleted


def test_a_thing_deleted_with_what_it_holds_shares_one_timestamp(storage_location_shelf):
    stamp = storage_location_shelf.location.soft_delete()
    storage_location_shelf.shelf.soft_delete(stamp)
    storage_location_shelf.soft_delete(stamp)

    assert storage_location_shelf.location.deleted_at == storage_location_shelf.shelf.deleted_at == stamp
    assert storage_location_shelf.deleted_at == stamp


def test_a_shelf_is_not_default_and_fills_back_left_horizontally_at_first(storage_shelf, storage_location):
    assert storage_shelf.is_default is False and storage_location.is_default is False
    assert storage_shelf.fill_order.value == 'back_left_horizontal'


def test_a_user_made_directly_has_no_external_account(user):
    assert user.external_accounts == []


def test_a_user_made_through_a_provider_has_an_external_account():
    from cynthus.core.user import ExternalAccount

    linked = UserFactory(external_accounts=[ExternalAccount(provider='google-oauth2', subject='1234')])

    assert [(a.provider, a.subject) for a in linked.external_accounts] == [('google-oauth2', '1234')]
    assert User.model_validate_json(linked.model_dump_json()) == linked
