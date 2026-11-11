"""User resource model class for the Cynthus project"""

from uuid import UUID, uuid4

from pydantic import Field

from ..soft_deletable import SoftDeletable


class User(SoftDeletable):
    """Represents a user resource"""

    id_: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: str
