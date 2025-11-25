from datetime import datetime
from typing import Annotated, Any, Optional, Union

from pydantic import BaseModel
from pydantic.types import FileUrl, HttpUrl

from ._common import BaseNode


class Article(BaseNode, BaseModel):
    """Structure of a Article Node in the Database"""

    title: str
    content: str
    published_date: datetime
    url: Optional[Annotated[HttpUrl, HttpUrl(user_info=None)]] = None
    authors: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None
    images: Optional[Union[Annotated[HttpUrl, HttpUrl(user_info=None)], FileUrl]] = None
