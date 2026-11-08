"""Audit Identity Email Signal Base class for the Cynthus project"""

from .audit_identity_base import AuditIdentitySignalBase


class AuditIdentityEmailSignalBase(AuditIdentitySignalBase, abstract=True):
    """Intermediate base for all audit identity email signals. Sets the aggregate component."""

    aggregate = 'email'
