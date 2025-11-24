from typing import Literal, cast

from flair.data import Sentence
from flair.models import SequenceTagger
from typing_extensions import override

from modules.ner._base import BaseClass
from type.article import Entity, EntityType


class FlairEntityModel(BaseClass):
    """NER Model Class for Flair Models"""

    __tagger: SequenceTagger

    def __init__(
        self,
        model: Literal[
            "ner-english-ontonotes", "ner-english-ontonotes-large"
        ] = "ner-english-ontonotes-large",
    ):
        """Initialize Flair Model Class"""
        self.__tagger = SequenceTagger.load(f"flair/{model}")

    @override
    def get_entities_from_text(self, text: str) -> list[Entity]:
        """Extract Entities from raw text

        Args:
            text (str): The text of which te entities need to be extracted

        Returns:
            list[Entity]: A list of `Entity` Objects
        """
        sentence = Sentence(text)
        self.__tagger.predict(sentence)
        entities = [
            Entity(word=ent.text, type=cast(EntityType, ent.get_label().value))
            for ent in sentence.get_spans("ner")
        ]
        return entities
