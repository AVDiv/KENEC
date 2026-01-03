from abc import ABC, abstractmethod

from type.article import Keyword


class BaseClass(ABC):
    """Base Class for Keyword Extractors Classes"""

    @abstractmethod
    def __init__(self):
        """Initialize Model Class"""
        raise NotImplementedError

    @abstractmethod
    async def get_keywords_from_text(self, text: str) -> list[Keyword]:
        """Extract Keywords from raw text

        Args:
            text (str): The text of which the keywords need to be extracted

        Returns:
            list[Keyword]: A list of `Keyword` Objects
        """
        raise NotImplementedError
