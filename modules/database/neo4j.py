# from modal.database.node import (
#     Article,
#     ArticleGroup,
#     Entity,
#     EntityGroup,
#     KeywordGroup,
#     Source,
# )
import logging
from datetime import date, datetime, time, timedelta
from typing import Any, List, Optional, Union, get_args, get_origin, override

from neo4j import Driver, EagerResult, GraphDatabase, Query
from pydantic import HttpUrl

from errors.database import (
    DatabaseConnectionAlreadyExists,
    DatabaseConnectionError,
    DatabaseMigrationError,
)
from modal.database.node._common import BaseNode
from modules.database._base import BaseAdapter
from type import (
    INDEXED,
    PRIMARY_KEY,
    REQUIRED,
    UNIQUE,
    UNIQUE_INDEXED,
    UNIQUE_REQUIRED,
    NodeType,
)
from type.database import DatabaseVariant


class Neo4jAdapter(BaseAdapter[Driver]):
    """Database Adapter for Neo4J"""

    __conn_uri: str
    __conn_username: str
    __conn_password: str
    __conn_dbname: str
    __conn_driver: Driver
    __created_initial_connection: bool
    __DATABASE_VARIANT: DatabaseVariant = "neo4j"

    def __init__(self, uri: str, username: str, password: str, database: str):
        super().__init__(uri, username, password, database)
        self.__conn_uri = uri
        self.__conn_username = username
        self.__conn_password = password
        self.__conn_dbname = database
        self.__created_initial_connection = False

    @override
    def _verify_connection(self) -> tuple[bool, Optional[Exception]]:
        try:
            self.__conn_driver.verify_connectivity()
            return (True, None)
        except Exception as e:
            return (False, e)

    @override
    def _verify_authentication(self) -> tuple[bool, Optional[Exception]]:
        try:
            self.__conn_driver.verify_authentication()
            return (True, None)
        except Exception as e:
            return (False, e)

    @override
    def connect(
        self,
    ) -> Optional[Union[DatabaseConnectionError, DatabaseConnectionAlreadyExists]]:
        # Check if connection was already made and still alive
        if self.__created_initial_connection:
            is_connected, connection_error = self._verify_connection()
            is_authenticated, authentication_error = self._verify_authentication()
            if is_connected and is_authenticated:
                return DatabaseConnectionAlreadyExists()
            try:
                self.__conn_driver.close()
            except Exception as e:
                logging.debug("Failed to close existing Neo4j driver: %s", e)

        # Create new connection
        try:
            self.__conn_driver = GraphDatabase.driver(
                uri=self.__conn_uri,
                auth=(self.__conn_username, self.__conn_password),
                database=self.__conn_dbname,
            )
        except Exception as e:
            return DatabaseConnectionError(str(e), self.__DATABASE_VARIANT)

        self.__created_initial_connection = True
        # Check if the connection was successful
        is_connected, connection_error = self._verify_connection()
        is_authenticated, authentication_error = self._verify_authentication()
        if is_connected and is_authenticated:
            return None
        if not is_connected:
            message = (
                str(connection_error)
                if connection_error is not None
                else "Failure in connection"
            )
            return DatabaseConnectionError(message, self.__DATABASE_VARIANT)
        # Not authenticated
        message = (
            str(authentication_error)
            if authentication_error is not None
            else "Failure in authentication"
        )
        return DatabaseConnectionError(message, self.__DATABASE_VARIANT)

    def create_node(self, node: NodeType):
        raise NotImplementedError()
        if node.__dict__:
            pass

    @override
    def migrate(
        self,
    ) -> dict[str, tuple[str, Union[EagerResult, DatabaseMigrationError]]]:
        """Set Constraints/indexes and necessary configurations for the database"""

        def _pydantic_to_cypher_type(annotation: Any) -> str | None:
            """
            Maps Python/Pydantic type annotations to Neo4j Cypher property type strings
            for use in type constraints (REQUIRE n.prop IS TYPE ...).

            Returns None if the type cannot be mapped to a supported Cypher type constraint.
            Supports common Pydantic types used in your Article model.
            """
            origin = get_origin(annotation)
            args = get_args(annotation)

            # Handle Optional[T] → same type as T (existence handled separately)
            if origin is Union and len(args) == 2 and type(None) in args:
                inner = args[0] if args[0] is not type(None) else args[1]
                return _pydantic_to_cypher_type(inner)

            # Handle lists (must be homogeneous)
            if origin in (list, List):
                if not args:
                    return None  # generic list not supported
                inner_type = _pydantic_to_cypher_type(args[0])
                if inner_type is None:
                    return None
                return f"LIST<{inner_type} NOT NULL>"

            # Direct type mappings
            if annotation is str or annotation == HttpUrl:  # HttpUrl is subclass of str
                return "STRING"

            if annotation is int:
                return "INTEGER"

            if annotation is float:
                return "FLOAT"

            if annotation is bool:
                return "BOOLEAN"

            if annotation is datetime:
                return "ZONED DATETIME"  # most common for published dates

            if annotation is date:
                return "DATE"

            if annotation is time:
                return "ZONED TIME"

            if annotation is timedelta:
                return "DURATION"

            return None  # Skip unsupported types (e.g. dict, Any, complex unions)

        def result_derivition(
            const_idx_name: str,
            query_response: Optional[EagerResult],
        ) -> tuple[str, Union[EagerResult, DatabaseMigrationError]]:
            if isinstance(query_response, EagerResult):
                if query_response.summary.gql_status_objects[0].gql_status.startswith(
                    "00"
                ):
                    res = (
                        const_idx_name,
                        query_response,
                    )
                else:
                    res = (
                        const_idx_name,
                        DatabaseMigrationError(
                            query_response.summary.gql_status_objects[
                                0
                            ].status_description
                        ),
                    )
            else:
                res = (
                    const_idx_name,
                    DatabaseMigrationError(),
                )
            return res

        query_results = {}
        for node_cls in BaseNode.all_node_classes():
            label = node_cls.__name__
            for name, field in node_cls.model_fields.items():
                # Parameter Definition
                parameters = {
                    "typeConstName": f"type_{label}_{name}".replace(
                        "\\u0060", "`"
                    ).replace("`", "``"),
                    "constIdxName": f"{label}_{name}".replace("\\u0060", "`").replace(
                        "`", "``"
                    ),
                    "label": label.replace("\\u0060", "`").replace("`", "``"),
                    "property": name.replace("\\u0060", "`").replace("`", "``"),
                }
                # Type (Constraint) Migration
                ## Skip if no type annotations to be migrated
                if field.annotation is not None:
                    cypher_type = _pydantic_to_cypher_type(field.annotation)
                    if cypher_type is not None:
                        cypher_type = cypher_type.replace("\\u0060", "`").replace(
                            "`", "``"
                        )
                        type_query_result = self.__conn_driver.execute_query(
                            query_=f"""
                            CREATE CONSTRAINT `{parameters["typeConstName"]}`
                            IF NOT EXISTS
                            FOR (n:`{parameters["label"]}`) REQUIRE n.`{parameters["property"]}` IS :: {cypher_type}
                            """,
                        )  # ty:ignore[no-matching-overload]

                        query_results[f"{label}::{name}::type"] = result_derivition(
                            cypher_type, type_query_result
                        )

                # Constraint Migration
                query_result = None
                ## Skip if no constraints/indexes to be migrated
                if not isinstance(field.json_schema_extra, dict):
                    continue
                const_idx = field.json_schema_extra.get("metadata")
                if not isinstance(const_idx, dict):
                    continue
                ## Definition
                if PRIMARY_KEY.items() <= const_idx.items():
                    const_idx_name = "PRIMARY_KEY"
                    def_type = "constraint"
                    query_result = self.__conn_driver.execute_query(
                        query_=f"""
                        CREATE CONSTRAINT `{parameters["constIdxName"]}`
                        IF NOT EXISTS
                        FOR (n:`{parameters["label"]}`) REQUIRE n.`{parameters["property"]}` IS NODE KEY
                        """
                    )  # ty:ignore[no-matching-overload]
                elif UNIQUE_INDEXED.items() <= const_idx.items():
                    const_idx_name = "UNIQUE_INDEXED"
                    def_type = "constraint"
                    query_result = self.__conn_driver.execute_query(
                        query_=f"""
                        CREATE CONSTRAINT `{parameters["constIdxName"]}`
                        IF NOT EXISTS
                        FOR (n:`{parameters["label"]}`) REQUIRE n.`{parameters["property"]}` IS UNIQUE
                        """
                    )  # ty:ignore[no-matching-overload]
                elif UNIQUE_REQUIRED.items() <= const_idx.items():
                    const_idx_name = "UNIQUE_REQUIRED"
                    def_type = "constraint"
                    query_result = self.__conn_driver.execute_query(
                        query_=f"""
                        CREATE CONSTRAINT `{parameters["constIdxName"]}`
                        IF NOT EXISTS
                        FOR (n:`{parameters["label"]}`)
                        REQUIRE (n.`{parameters["property"]}` IS NOT NULL AND n.`{parameters["property"]}` IS UNIQUE)
                        """,
                    )  # ty:ignore[no-matching-overload]

                elif INDEXED.items() <= const_idx.items():
                    const_idx_name = "INDEXED"
                    def_type = "index"
                    query_result = self.__conn_driver.execute_query(  # Note: added assignment for consistency
                        query_=f"""
                        CREATE RANGE INDEX `{parameters["constIdxName"]}`
                        IF NOT EXISTS
                        FOR (n:`{parameters["label"]}`) ON (n.`{parameters["property"]}`)
                        """,
                    )  # ty:ignore[no-matching-overload]

                elif UNIQUE.items() <= const_idx.items():
                    const_idx_name = "UNIQUE"
                    def_type = "constraint"
                    query_result = self.__conn_driver.execute_query(
                        query_=f"""
                        CREATE CONSTRAINT `{parameters["constIdxName"]}`
                        IF NOT EXISTS
                        FOR (n:`{parameters["label"]}`)
                        REQUIRE n.`{parameters["property"]}` IS UNIQUE
                        """,
                    )  # ty:ignore[no-matching-overload]

                elif REQUIRED.items() <= const_idx.items():
                    const_idx_name = "REQUIRED"
                    def_type = "constraint"
                    query_result = self.__conn_driver.execute_query(
                        query_=f"""
                        CREATE CONSTRAINT `{parameters["constIdxName"]}`
                        IF NOT EXISTS
                        FOR (n:`{parameters["label"]}`)
                        REQUIRE n.`{parameters["property"]}` IS NOT NULL
                        """,
                    )  # ty:ignore[no-matching-overload]
                query_results[f"{label}::{name}::{def_type}"] = result_derivition(
                    const_idx_name, query_result
                )
        return query_results
