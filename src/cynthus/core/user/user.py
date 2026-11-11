"""User resource model class for the Cynthus project"""

from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class User(BaseModel):
    """Represents a user resource"""

    id_: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: str
