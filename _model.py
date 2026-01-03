import asyncio
import logging
from threading import Thread
from types import CoroutineType
from typing import Any, Literal, Optional, Union

from pydantic import AnyUrl, SecretStr

from errors.database import (
    DatabaseConnectionAlreadyExists,
    DatabaseConnectionError,
    DatabaseMigrationError,
    DatabaseRequiredCredentialsMissingError,
)
from errors.kenec import CannotClusterArticleError
from modal.database.node import Article
from modal.database.util.auth import DatabaseAuth
from modules.database import Neo4jAdapter
from modules.keyword_extractor import YakeKeywordExtractor
from modules.ner import (
    FlairEntityModel,
    SpacyEntityModel,
    XlmRobertaLargeFinetunedConll03EnglishEntityModel,
)
from type.article import Entity, Keyword
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
    __unit_intializers: list[Thread]

    def __init__(
        self,
        *,
        match_threshold: float = 0.87,
        ner_model: NERModelOption = "xlm_roberta_large_finetuned",
        kw_extractor: KeywordExtractorOption = "yake",
        database: DatabaseVariant = "neo4j",
        db_auth: DatabaseAuth,
        prepare_db: bool = True,
    ):
        """Initialize the model with preferences

        Args:
            match_threshold (float): A threshold to match in which a matching news group is determined (Should be a value between 0 and 1).
        """
        logging.info(f"Initializing KENEC model {self.__str__()}")
        self.match_threshold = self.__validate_match_threshold(match_threshold)
        unit_init_functions = [
            (
                self.__initialize_database_from_option,
                [database],
                (db_auth.__dict__),
                "database",
            ),
            (
                self.__initialize_kw_extractor_from_option,
                [kw_extractor],
                None,
                "kw_extractor",
            ),
            (self.__initialize_ner_model_from_option, [ner_model], None, "ner"),
        ]
        __unit_intializers = []
        for func, args, kwargs, name_suffix in unit_init_functions:
            unit_thread = Thread(
                target=func, args=args, kwargs=kwargs, name=f"kenec_{name_suffix}_unit"
            )
            unit_thread.start()
            __unit_intializers.append(unit_thread)
        db_unit_thread = __unit_intializers.pop(0)
        db_unit_thread.join()
        if prepare_db:
            asyncio.run(self.prepare_database())
        for unit_thread in __unit_intializers:
            unit_thread.join()

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

    def __initialize_ner_model_from_option(self, option: NERModelOption):
        """Initializes the NER Model class for the selected option

        Args:
            option (NERModelOption): NER Option
        """
        if option == "xlm_roberta_large_finetuned":
            self.__entity_extractor = (
                XlmRobertaLargeFinetunedConll03EnglishEntityModel()
            )
        elif option == "spacy_web_sm":
            self.__entity_extractor = SpacyEntityModel(model="en_core_web_sm")
        elif option == "spacy_web_md":
            self.__entity_extractor = SpacyEntityModel(model="en_core_web_md")
        elif option == "spacy_web_lg":
            self.__entity_extractor = SpacyEntityModel(model="en_core_web_lg")
        elif option == "spacy_web_trf":
            self.__entity_extractor = SpacyEntityModel(model="en_core_web_trf")
        elif option == "flair_english_ontonotes":
            self.__entity_extractor = FlairEntityModel(model="ner-english-ontonotes")
        elif option == "flair_english_ontonotes_large":
            self.__entity_extractor = FlairEntityModel(
                model="ner-english-ontonotes-large"
            )
        else:
            raise ValueError(f"Invalid option selection '{option}'")

    def __initialize_kw_extractor_from_option(
        self,
        option: KeywordExtractorOption,
    ):
        """Initializes the Keyword Extractor class for the selected option

        Args:
            option (KeywordExtractorOption): Keyword Extractor Option
        """
        if option == "yake":
            self.__keyword_extractor = YakeKeywordExtractor()
        else:
            raise ValueError(f"Invalid option selection '{option}'")

    def __initialize_database_from_option(
        self,
        option: DatabaseVariant,
        **kwargs,
    ):
        """Initializes the Database class for the selected option

        Args:
            option (DatabaseOption): Database Option
        """
        if option == "neo4j":
            required_params: set[str] = {"uri", "username", "password", "database"}
            key_set = set(kwargs.keys())
            if key_set <= required_params:
                missing = required_params - key_set
                error = DatabaseRequiredCredentialsMissingError(missing, "neo4j")
                logging.error(
                    f"Missing required database credentials:: {error.__str__()}"
                )
                raise error
            # Type conversions
            kwargs["uri"] = (
                kwargs["uri"].unicode_string()
                if isinstance(kwargs["uri"], AnyUrl)
                else kwargs["uri"]
            )
            kwargs["password"] = (
                kwargs["password"].get_secret_value()
                if isinstance(kwargs["password"], SecretStr)
                else kwargs["password"]
            )
            self.__database = Neo4jAdapter(
                uri=kwargs["uri"],
                username=kwargs["username"],
                password=kwargs["password"],
                database=kwargs["database"],
            )
        else:
            logging.error(f"Invalid database option: {option}")
            raise ValueError(f"Invalid option selection '{option}'")

    async def prepare_database(self):
        """Prepare/Setup the database for usage

        Raises:
            DatabaseConnectionAlreadyExists: The database connection has been already initialized and is still alive.
            DatabaseConnectionError: The database adapter failed to connect to the database. Probably caused by authentication (provided invalid credentials) or network issues.
            DatabaseMigrationError: Failed to migrate the configurations to the connected database.
        """
        logging.debug("Preparing the database...")
        # Connect to the database
        connection_error = await self.__database.connect()

        if connection_error is None:
            logging.info("Succesfully connected to graph database!")
        elif isinstance(connection_error, DatabaseConnectionError) or isinstance(
            connection_error, DatabaseConnectionAlreadyExists
        ):
            logging.error(connection_error)
            raise connection_error
        else:
            logging.error("Unhandled exception occured when connecting to the database")
            raise connection_error
        # Migrate configurations to the database
        migration_results = await self.__database.migrate()
        for key, (constraint, result) in migration_results.items():
            label, field, def_type = key.split("::")
            if isinstance(result, DatabaseMigrationError):
                logging.warning(
                    f"Failed initialization of '{constraint}' {def_type} for '{field}' in '{label}' {':: {}'.format(result.__str__()) if result.__str__() != 'None' else ''}"
                )
            else:
                logging.debug(
                    f"Succesfully initialized '{constraint}' {def_type} for '{field}' in '{label}'"
                )

    async def add_article(
        self, news_article: Article
    ) -> tuple[list[Keyword], list[Entity]]:
        """Add a new article to be clustered

        Args:
            news_article (NewsArticle): The new News Article's data

        Returns:
            tuple[list[Keyword], list[Entity]]: Extracted keywords and entities from the article.
        """
        merged_article_content: str = news_article.title + "\n" + news_article.content

        # Extract keywords and entities
        kw_coro: CoroutineType[Any, Any, list[Keyword]] = (
            self.__keyword_extractor.get_keywords_from_text(text=merged_article_content)
        )
        ent_coro: CoroutineType[Any, Any, list[Entity]] = (
            self.__entity_extractor.get_entities_from_text(text=merged_article_content)
        )

        article_keywords, article_entities = await asyncio.gather(kw_coro, ent_coro)

        logging.debug(
            "Extracted %d keywords and %d entities for article '%s'",
            len(article_keywords),
            len(article_entities),
            getattr(news_article, "title", "UNKNOWN"),
        )

        # If no entities or keywords
        no_keywords = not article_keywords
        no_entites = not article_entities
        if no_entites or no_keywords:
            logging.error(
                "Article '%s' did not yield either of entities or keywords, Cannot group this articles. Skipping...",
                getattr(news_article, "title", "UNKNOWN"),
            )
            raise CannotClusterArticleError(
                "No Entites or Keywords found to group this article."
            )

        return article_keywords, article_entities

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
