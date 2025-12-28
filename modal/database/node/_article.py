from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, FileUrl, HttpUrl

from type import REQUIRED, UNIQUE

from ._common import BaseNode


class Article(BaseNode, BaseModel):
    """Structure of a Article Node in the Database"""

    title: str = Field(..., metadata=REQUIRED)
    content: str = Field(..., metadata=REQUIRED)
    published_date: datetime = Field(..., metadata=REQUIRED)
    url: Optional[HttpUrl] = Field(..., metadata=UNIQUE)
    authors: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None
    images: Optional[list[Union[HttpUrl, FileUrl]]] = None
