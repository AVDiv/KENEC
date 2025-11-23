from typing import Literal, cast

import spacy
from spacy import Language
from spacy.cli import download as spacy_model_download
from typing_extensions import override

from modules.ner._base import BaseClass
from type.article import Entity, EntityType


class SpacyEntityModel(BaseClass):
    """NER Model Class for Spacy Models"""

    __pipeline: Language

    def __init__(
        self,
        model: Literal[
            "en_core_web_sm", "en_core_web_md", "en_core_web_lg", "en_core_web_trf"
        ],
    ):
        """Initialize Spacy Model Class"""
        spacy_model_download(model)
        self.__pipeline = spacy.load(model)
        _ = self.__pipeline.select_pipes(enable="ner")

    @override
    def get_entities_from_text(self, text: str) -> list[Entity]:
        """Extract Entities from raw text

        Args:
            text (str): The text of which te entities need to be extracted

        Returns:
            list[Entity]: A list of `Entity` Objects
        """
        spacy_entities = self.__pipeline(text)
        entities = [
            Entity(word=ent.text, type=cast(EntityType, ent.label_))
            for ent in spacy_entities.ents
        ]
        return entities
