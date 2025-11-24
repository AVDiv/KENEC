from typing_extensions import override
from yake import KeywordExtractor

from type.article import Keyword

from ._base import BaseClass


class YakeKeywordExtractor(BaseClass):
    """Base Class for Keyword Extractors Classes"""

    __extractor: KeywordExtractor

    def __init__(self):
        """Initialize Model Class"""
        self.__extractor = KeywordExtractor()

    @override
    def get_keywords_from_text(self, text: str) -> list[Keyword]:
        """Extract Keywords from raw text

        Args:
            text (str): The text of which the keywords need to be extracted

        Returns:
            list[Keyword]: A list of `Keyword` Objects
        """
        keywords = self.__extractor.extract_keywords(text)
        return [Keyword(word=keyword[0], score=keyword[1]) for keyword in keywords]
