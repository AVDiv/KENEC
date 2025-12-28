from abc import ABC
from datetime import datetime
from functools import cache
from typing import Annotated, Optional, Type
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.types import UuidVersion

from type import PRIMARY_KEY, REQUIRED

_registry: set[Type["BaseNode"]] = set()


class BaseNode(BaseModel, ABC):
    """Base Structure of a Node in the Database"""

    id: Optional[Annotated[UUID, UuidVersion(4)]] = Field(..., metadata=PRIMARY_KEY)
    created_on: Optional[datetime] = Field(..., metadata=REQUIRED)
    updated_on: Optional[datetime] = Field(..., metadata=REQUIRED)

    @classmethod
    @cache
    def node_type(cls) -> str:
        return cls.__name__

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is not BaseNode:  # don't register BaseNode itself
            _registry.add(cls)

    @classmethod
    def all_node_classes(cls) -> list[Type["BaseNode"]]:
        """Return all registered node model classes"""
        return list(_registry)

    @classmethod
    def get_by_label(cls, label: str) -> Type["BaseNode"] | None:
        """Get class by node label (e.g. 'Article')"""
        return next((c for c in _registry if c.__name__ == label), None)
