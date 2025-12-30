"""
Database-Related Exceptions
"""

from typing import Optional

from type.database import DatabaseVariant


class DatabaseError(Exception):
    """A Database Related Error"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message)


# ================== Credentials Errors ==================
class DatabaseRequiredCredentialsMissingError(DatabaseError):
    """Required credentials are not provided"""

    def __init__(self, field: set[str], database_variant: DatabaseVariant):
        super().__init__(
            f"Parameter `{', '.join(field)}` is required for {database_variant}"
        )


# ================== Connection Errors ==================
class DatabaseConnectionError(DatabaseError):
    """Failed to connect to the database"""

    def __init__(self, message: str, database_variant: DatabaseVariant):
        super().__init__(
            f"Failed to connect to {database_variant} instance:: {message}"
        )


class DatabaseConnectionAlreadyExists(DatabaseError):
    """Tried to create an additional database connection while a connection exists"""


# ================== Migration Errors ==================
class DatabaseMigrationError(DatabaseError):
    """Failed to create a constraint on migration"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message)
