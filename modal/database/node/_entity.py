from pydantic import BaseModel

from ._common import BaseNode


class EntityGroup(BaseNode, BaseModel):
    """Structure of a Entity Node in the Database"""

    entity_type: str
