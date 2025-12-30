import re
from typing import Annotated, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, SecretStr, TypeAdapter, field_validator
from pydantic.types import StringConstraints


class DatabaseAuth(BaseModel):
    """Database credentials manager

    Args:
        `uri` (Union[AnyUrl, str]): URI of the database instance
        `username` (str): Username of the database account
        `password` (Union[SecretStr, str]): Password of the database account
        `database` (str): Name of the database
        `realm` (Optional[str]): ...
    """

    uri: Union[AnyUrl, str] = AnyUrl("neo4j://localhost:7687")
    username: str
    password: Union[SecretStr, str]
    database: str
    realm: Optional[str] = None

    @field_validator("uri")
    @classmethod
    def validate_neo4j_uri(cls, v: AnyUrl) -> AnyUrl:
        allowed_schemes = {
            "bolt",
            "bolt+s",
            "bolt+ssc",
            "neo4j",
            "neo4j+s",
            "neo4j+ssc",
        }
        if isinstance(v, str):
            ta = TypeAdapter(AnyUrl)
            v = ta.validate_strings(v)
        if v.scheme not in allowed_schemes:
            raise ValueError(
                f"Invalid Neo4j URI scheme '{v.scheme}'. "
                f"Must be one of: {', '.join(sorted(allowed_schemes))}"
            )
        return v

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Neo4j username cannot be empty")
        return v.strip()

    @field_validator("database")
    @classmethod
    def database_name_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Database name cannot be empty")
        return v

    @field_validator("realm")
    @classmethod
    def realm_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Realm cannot be empty if provided")
            if not re.fullmatch(r"[a-zA-Z0-9\._-]+", v):
                raise ValueError("Realm contains invalid characters")
        return v

    model_config = {
        "frozen": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
