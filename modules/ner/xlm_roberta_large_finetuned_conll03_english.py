import re

from transformers import TokenClassificationPipeline, pipeline
from typing_extensions import override

from modules.ner._base import BaseClass
from type.article import Entity


class XlmRobertaLargeFinetunedConll03EnglishEntityModel(BaseClass):
    """NER Model Class for FacebookAI/xlm-roberta-large-finetuned-conll03-english"""

    __pipeline: TokenClassificationPipeline

    def __init__(self):
        self.__pipeline = pipeline(
            "token-classification",
            model="FacebookAI/xlm-roberta-large-finetuned-conll03-english",
        )

    @override
    async def get_entities_from_text(self, text: str) -> list[Entity]:
        """Extract Entities from raw text

        Args:
            text (str): The text of which te entities need to be extracted

        Returns:
            list[Entity]: A list of `Entity` Objects
        """
        pipeline_entites = self.__pipeline(text)
        combined_entities = await self.__combine_same_entities(text, pipeline_entites)

        result_entities: list = []
        for combined_entity_dict in combined_entities:
            original_entity_type = combined_entity_dict["entity"]
            if original_entity_type == "I-PER":
                entity_type = "PERSON"
            elif original_entity_type == "I-LOC":
                entity_type = "LOC"
            elif original_entity_type == "I-ORG":
                entity_type = "ORG"
            elif original_entity_type == "I-MISC":
                entity_type = "MISC"
            else:
                continue
            result_entities.append(
                Entity(
                    word=combined_entity_dict["word"],
                    type=entity_type,
                )
            )
        return result_entities

    async def __combine_same_entities(
        self, text: str, raw_entities: list[dict]
    ) -> list[dict]:
        prev_segment = None
        entities = []
        for segment in raw_entities:
            segment["word"] = segment["word"].replace("▁", " ")
            original_entity_word = segment["word"]
            entity_word = segment["word"].rstrip()
            segment["end"] = segment["end"] - (
                len(original_entity_word) - len(entity_word)
            )
            if segment["word"].isspace():
                continue
            appended_to_prev_segment = False
            if prev_segment is not None and prev_segment["entity"] == segment["entity"]:
                if prev_segment["end"] == segment["start"]:
                    entities[-1]["word"] += segment["word"]
                    appended_to_prev_segment = True
                elif text[prev_segment["end"] : segment["start"]].isspace():
                    entities[-1]["word"] += (
                        text[prev_segment["end"] : segment["start"]] + segment["word"]
                    )
                    appended_to_prev_segment = True

                if appended_to_prev_segment:
                    entities[-1]["end"] = segment["end"]
                    entities[-1]["score"] = (
                        entities[-1]["score"] + segment["score"]
                    ) / 2

            if not appended_to_prev_segment:
                original_entity_word = entity_word
                entity_word = entity_word.lstrip()
                segment["start"] = segment["start"] + (
                    len(original_entity_word) - len(entity_word)
                )
                entities.append(
                    {
                        "entity": segment["entity"],
                        "word": entity_word,
                        "score": segment["score"],
                        "start": segment["start"],
                        "end": segment["end"],
                    }
                )
            entities[-1]["word"] = re.sub(r" +", " ", entities[-1]["word"]).strip()
            prev_segment = segment.copy()
        return entities
