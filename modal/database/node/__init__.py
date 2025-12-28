from typing import Union

from ._article import Article
from ._article_group import ArticleGroup
from ._entity import Entity
from ._entity_group import EntityGroup
from ._keyword_group import KeywordGroup
from ._source import Source

NodeType = Union[Article, ArticleGroup, Source, Entity, EntityGroup, KeywordGroup]

__all__ = [
    "Article",
    "ArticleGroup",
    "Entity",
    "EntityGroup",
    "KeywordGroup",
    "Source",
    "NodeType",
]
