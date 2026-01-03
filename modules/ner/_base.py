from abc import ABC, abstractmethod

from type.article import Entity


class BaseClass(ABC):
    """Base Class for NER Model Classes"""

    @abstractmethod
    def __init__(self):
        """Initialize Model Class"""
        raise NotImplementedError

    @abstractmethod
    async def get_entities_from_text(self, text: str) -> list[Entity]:
        """Extract Entities from raw text

        Args:
            text (str): The text of which te entities need to be extracted

        Returns:
            list[Entity]: A list of `Entity` Objects
        """
        raise NotImplementedError
