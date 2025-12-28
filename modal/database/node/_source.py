from typing import Any, Optional

from pydantic import BaseModel, HttpUrl

from ._common import BaseNode


class Source(BaseNode, BaseModel):
    """Structure of a Source Node in the Database"""

    name: str
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    metadata: Optional[dict[str, Any]] = None
