from pydantic import BaseModel

from ._common import BaseNode


class ArticleGroup(BaseNode, BaseModel):
    """Structure of a Article Group Node in the Database"""

    total_entity_scorable: float
    total_keyword_scorable: float
