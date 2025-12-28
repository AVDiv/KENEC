from typing import Literal

from typing_extensions import TypedDict


class IndexConstraintType(TypedDict, total=False):
    indexed: Literal[True]  # Index
    unique: Literal[True]  # Unique Constraint
    existence: Literal[True]  # Existence Constraint


# Marker constants
UNIQUE = IndexConstraintType(unique=True)
INDEXED = IndexConstraintType(indexed=True)
REQUIRED = IndexConstraintType(existence=True)
UNIQUE_REQUIRED = IndexConstraintType(unique=True, existence=True)
UNIQUE_INDEXED = IndexConstraintType(unique=True, indexed=True)
PRIMARY_KEY = IndexConstraintType(unique=True, indexed=True, existence=True)
