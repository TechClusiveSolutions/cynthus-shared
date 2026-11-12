"""Tests for cynthus.messaging.common.signal.public_auth_workspace_role_created."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_auth_workspace_role_base import PublicAuthWorkspaceRoleSignalBase
from cynthus.messaging.common.signal.public_auth_workspace_role_created import PublicAuthWorkspaceRoleCreatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicAuthWorkspaceRoleCreatedSignal.name == 'public.auth.workspace_role.created'


def test_components():
    assert PublicAuthWorkspaceRoleCreatedSignal.visibility == 'public'
    assert PublicAuthWorkspaceRoleCreatedSignal.domain is SignalDomainType.AUTH
    assert PublicAuthWorkspaceRoleCreatedSignal.aggregate == 'workspace_role'
    assert PublicAuthWorkspaceRoleCreatedSignal.action is SignalActionType.CREATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicAuthWorkspaceRoleCreatedSignal, PublicAuthWorkspaceRoleSignalBase)
    assert issubclass(PublicAuthWorkspaceRoleCreatedSignal, SignalBase)
