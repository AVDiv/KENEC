from threading import Thread
from typing import Literal, Union

from errors.database import DatabaseRequiredCredentialsMissingError
from modal.database.node import Article
from modal.database.util.auth import DatabaseAuth
from modules.database import Neo4jAdapter
from modules.keyword_extractor import YakeKeywordExtractor
from modules.ner import (
    FlairEntityModel,
    SpacyEntityModel,
    XlmRobertaLargeFinetunedConll03EnglishEntityModel,
)
from type.database import DatabaseVariant

NERModelClass = Union[
    SpacyEntityModel,
    FlairEntityModel,
    XlmRobertaLargeFinetunedConll03EnglishEntityModel,
]
KeywordExtractorClass = Union[YakeKeywordExtractor]
DatabaseClass = Union[Neo4jAdapter]

NERModelOption = Literal[
    # Hugging face models
    "xlm_roberta_large_finetuned",
    # Spacy Models
    "spacy_web_sm",
    "spacy_web_md",
    "spacy_web_lg",
    "spacy_web_trf",
    # Flair Models
    "flair_english_ontonotes",
    "flair_english_ontonotes_large",
]
KeywordExtractorOption = Literal["yake"]


class KENEC:
    """The Keyword-Entity News Event Clustering Model"""

    __entity_extractor: NERModelClass
    __keyword_extractor: KeywordExtractorClass
    __database: DatabaseClass
    match_threshold: float

    def __init__(
        self,
        *,
        match_threshold: float,
        ner_model: NERModelOption,
        kw_extractor: KeywordExtractorOption,
        database: DatabaseVariant = "neo4j",
        db_auth: DatabaseAuth,
    ):
        """Initialize the model with preferences

        Args:
            match_threshold (float): A threshold to match in which a matching news group is determined (Should be a value between 0 and 1).
        """
        self.match_threshold = self.__validate_match_threshold(match_threshold)
        self.__entity_extractor = self.__fetch_ner_model_from_option(ner_model)
        self.__keyword_extractor = self.__fetch_kw_extractor_from_option(kw_extractor)
        self.__database = self.__fetch_database_from_option(
            option=database, kwargs=db_auth.__dict__
        )

    def __validate_match_threshold(self, v: float):
        """The validator to determine if the given match threshold is a valid value

        Args:
            v (float): Threshold value

        Returns:
            v (float): Threshold value

        Raises:
            ValueError: If match threshold is not a float
            ValueError: If match threshold is not a value > 0
            ValueError: If match threshold is not a a value <= 1
        """
        if not (isinstance(v, float) or isinstance(v, int)):
            raise ValueError("Match threshold should be a float")
        if v <= 0:
            raise ValueError("Match threshold should be a value > 0")
        elif v > 1:
            raise ValueError("Match threshold should be a value between 0 and 1")
        return v

    def __fetch_ner_model_from_option(self, option: NERModelOption) -> NERModelClass:
        """Fetch the NER Model class for the selected option

        Args:
            option (NERModelOption): NER Option

        Return:
            NERModelClass: The Model instance
        """
        if option == "xlm_roberta_large_finetuned":
            return XlmRobertaLargeFinetunedConll03EnglishEntityModel()
        elif option == "spacy_web_sm":
            return SpacyEntityModel(model="en_core_web_sm")
        elif option == "spacy_web_md":
            return SpacyEntityModel(model="en_core_web_md")
        elif option == "spacy_web_lg":
            return SpacyEntityModel(model="en_core_web_lg")
        elif option == "spacy_web_trf":
            return SpacyEntityModel(model="en_core_web_trf")
        elif option == "flair_english_ontonotes":
            return FlairEntityModel(model="ner-english-ontonotes")
        elif option == "flair_english_ontonotes_large":
            return FlairEntityModel(model="ner-english-ontonotes-large")
        else:
            raise ValueError(f"Invalid option selection '{option}'")

    def __fetch_kw_extractor_from_option(
        self,
        option: KeywordExtractorOption,
    ) -> KeywordExtractorClass:
        """Fetch the Keyword Extractor class for the selected option

        Args:
            option (KeywordExtractorOption): Keyword Extractor Option

        Return:
            KeywordExtractorClass: The Model instance
        """
        if option == "yake":
            return YakeKeywordExtractor()
        else:
            raise ValueError(f"Invalid option selection '{option}'")

    def __fetch_database_from_option(
        self,
        option: DatabaseVariant,
        **kwargs,
    ) -> DatabaseClass:
        """Fetch the Database class for the selected option

        Args:
            option (DatabaseOption): Database Option

        Return:
            DatabaseClass: The Database instance
        """
        if option == "neo4j":
            required_params: set[str] = {"uri", "username", "password", "database"}

            if required_params not in kwargs.keys():
                missing = required_params - set(kwargs.keys())
                raise DatabaseRequiredCredentialsMissingError(missing, "neo4j")
            return Neo4jAdapter(
                uri=kwargs["uri"],
                username=kwargs["username"],
                password=kwargs["password"],
                database=kwargs["database"],
            )
        else:
            raise ValueError(f"Invalid option selection '{option}'")

    def add_article(self, news_article: Article):
        """Add a new article to be clustered

        Args:
            news_article (NewsArticle): The new News Article's data

        Returns:
            ????
        """
        merged_article_content: str = news_article.title + "\n" + news_article.content

        # Extract keywords and entities
        keyword_extractor_thread: Thread = Thread(
            target=self.__keyword_extractor.get_keywords_from_text,
            kwargs={"text": merged_article_content},
            name="keyword_extraction_task",
        )
        keyword_extractor_thread.run()
        entity_extractor_thread: Thread = Thread(
            target=self.__entity_extractor.get_entities_from_text,
            kwargs={"text": merged_article_content},
            name="entity_extraction_task",
        )
        entity_extractor_thread.run()

        # Assign to new group if no entities or keywords

    def __find_or_create_article_group(self, article: Article) -> tuple[str, bool]:
        """Find an existing article group for an article or create a new one

        Uses a two-step process:
        1. Shortlist candidate groups based on title similarity
        2. Apply detailed entity and keyword matching to find best group

        Args:
            article: Article's data
            entities: Derived entities from the Article
            keywords: Derived keywords from the Article

        Returns:
            tuple[str, bool]: Tuple of (group_id, is_new_group)
        """
        raise NotImplementedError()
