from abc import ABC, abstractmethod
from typing import TypeVar, Generic

DatabaseConnection = TypeVar("DatabaseConnection")


class BaseAdapter(ABC, Generic[DatabaseConnection]):
    """Base Adapter for Databases"""

    __conn_uri: str
    __conn_username: str
    __conn_password: str
    __conn_dbname: str
    __conn_driver: DatabaseConnection

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
    def __verify_connection(self) -> bool:
        """Verifies the connection to the database.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        pass

    @abstractmethod
    def __verify_authentication(self) -> bool:
        """Verifies the authentication to the database.

        Returns:
            bool: True if the authentication is successful, False otherwise.
        """
        pass

    @abstractmethod
    def connect(self) -> bool:
        """Connects to the database.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        pass
