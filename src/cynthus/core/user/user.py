"""User resource model class for the Cynthus project"""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents a user resource"""

    id_: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: str
