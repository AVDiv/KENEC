from pydantic import BaseModel

from ._common import BaseNode


class Entity(BaseNode, BaseModel):
    """Structure of a Entity Node in the Database"""

    word: str
