from typing import Annotated, Any, Optional

from pydantic import BaseModel
from pydantic.types import HttpUrl

from ._common import BaseNode


class Source(BaseNode, BaseModel):
    """Structure of a Source Node in the Database"""

    name: str
    description: Optional[str] = None
    url: Optional[Annotated[HttpUrl, HttpUrl(user_info=None)]] = None
    metadata: Optional[dict[str, Any]] = None
