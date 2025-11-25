from pydantic import BaseModel

from ._common import BaseNode


class EntityGroup(BaseNode, BaseModel):
    """Structure of a Entity Group Node in the Database"""

    entity_type: str
