"""Tests for cynthus.messaging.common.signal.public_auth_workspace_role_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_auth_workspace_role_base import PublicAuthWorkspaceRoleSignalBase
from cynthus.messaging.common.signal.public_auth_workspace_role_updated import PublicAuthWorkspaceRoleUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicAuthWorkspaceRoleUpdatedSignal.name == 'public.auth.workspace_role.updated'


def test_components():
    assert PublicAuthWorkspaceRoleUpdatedSignal.visibility == 'public'
    assert PublicAuthWorkspaceRoleUpdatedSignal.domain is SignalDomainType.AUTH
    assert PublicAuthWorkspaceRoleUpdatedSignal.aggregate == 'workspace_role'
    assert PublicAuthWorkspaceRoleUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicAuthWorkspaceRoleUpdatedSignal, PublicAuthWorkspaceRoleSignalBase)
    assert issubclass(PublicAuthWorkspaceRoleUpdatedSignal, SignalBase)
