"""
Database-Related Exceptions
"""

from typing import Optional


class KENECException(Exception):
    """KENEC Related Error"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message)


class CannotClusterArticleError(KENECException):
    """Cannot cluster this article"""

    def __init__(self, message: str):
        super().__init__(message)
