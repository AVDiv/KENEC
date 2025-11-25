from abc import ABC
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic.types import UuidVersion


class BaseNode(BaseModel, ABC):
    """Base Structure of a Node in the Database"""

    _id: Optional[Annotated[UUID, UuidVersion(4)]] = None
    _created_on: Optional[datetime] = None
    _updated_on: Optional[datetime] = None
