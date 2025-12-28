from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from type.database import DatabaseVariant

DatabaseConnection = TypeVar("DatabaseConnection")


class BaseAdapter(ABC, Generic[DatabaseConnection]):
    """Base Adapter for Databases"""

    __conn_uri: str
    __conn_username: str
    __conn_password: str
    __conn_dbname: str
    __conn_driver: DatabaseConnection
    __created_initial_connection: bool
    __DATABASE_VARIANT: DatabaseVariant

    @abstractmethod
    def __init__(self, uri: str, username: str, password: str, database: str):
        """Initializes the database adapter with connection details.

        Args:
            uri (str): The connection URI for the database.
            username (str): The username for connecting to the database.
            password (str): The password for connecting to the database.
            database (str): The name of the database.
        """
        pass

    @abstractmethod
    def _verify_connection(self) -> tuple[bool, Optional[Exception]]:
        """Verifies the connection to the database.

        Returns:
            tuple[bool, Optional[Exception]]: True if the connection is successful, False otherwise (with the exception).
        """
        pass

    @abstractmethod
    def _verify_authentication(self) -> tuple[bool, Optional[Exception]]:
        """Verifies the authentication to the database.

        Returns:
            tuple[bool, Optional[Exception]]: True if the authentication is successful, False otherwise (with the exception).
        """
        pass

    @abstractmethod
    def connect(self) -> Optional[Any]:
        """Connects to the database.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        pass

    @abstractmethod
    def migrate(self) -> dict[str, tuple[str, Any]]:
        """Set Constraints and necessary configurations for the database"""
        pass
