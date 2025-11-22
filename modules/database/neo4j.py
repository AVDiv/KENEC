from typing import override
from modules.database._base import BaseAdapter
from neo4j import Driver, GraphDatabase, Session


class Neo4jAdapter(BaseAdapter[Driver]):
    """Database Adapter for Neo4J"""

    __conn_uri: str
    __conn_username: str
    __conn_password: str
    __conn_dbname: str
    __conn_driver: Driver
    __conn_session: Session

    def __init__(self, uri: str, username: str, password: str, database: str):
        super().__init__(uri, username, password, database)
        self.__conn_uri = uri
        self.__conn_username = username
        self.__conn_password = password
        self.__conn_dbname = database
        self.__conn_driver = GraphDatabase.driver(uri, auth=(username, password))

    @override
    def __verify_connection(self) -> bool:
        try:
            self.__conn_driver.verify_connectivity()
            return True
        except Exception:
            return False

    @override
    def __verify_authentication(self) -> bool:
        try:
            self.__conn_driver.verify_authentication()
            return True
        except Exception:
            return False

    def create_session(self) -> Session:
        return self.__conn_driver.session(database=self.__conn_dbname)

    @override
    def connect(self) -> bool:
        # Check if the connection was successful
        is_success: bool = self.__verify_connection() and self.__verify_authentication()
        if is_success:
            self.__conn_session = self.create_session()
            return True
        else:
            return False
