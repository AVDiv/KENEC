from typing import Literal

from pydantic import BaseModel

EntityType = Literal[
    "PERSON",  # Person (People, including fictional.)
    "LOC",  # Location (Non-GPE locations, mountain ranges, bodies of water)
    "ORG",  # Organization (Companies, agencies, institutions, etc.)
    "CARDINAL",  # Cardinal (Numerals that do not fall under another type)
    "DATE",  # Date (Absolute or relative dates or periods)
    "EVENT",  # Event (Named hurricanes, battles, wars, sports events, etc.)
    "FAC",  # Buildings, airports, highways, bridges, etc.
    "GPE",  # Geo-Political Entity (Countries, cities, states)
    "LANGUAGE",  # Language (Any named language.)
    "LAW",  # Law (Named documents made into laws.)
    "MONEY",  # Money (Monetary values, including unit.)
    "NORP",  # Nationalities or religious or political groups.
    "ORDINAL",  # Ordinal (“first”, “second”, etc.)
    "PERCENT",  # Percentage, including ”%“
    "PRODUCT",  # Product (Objects, vehicles, foods, etc. (Not services.))
    "QUANTITY",  # Quantity (Measurements, as of weight or distance.)
    "TIME",  # Time (Times smaller than a day.)
    "WORK_OF_ART",  # Work of Art (Titles of books, songs, etc.)
    "MISC",  # Miscellanous (other)
]


class Entity(BaseModel):
    """Data Model for a Entity Instance"""

    word: str
    type: EntityType
