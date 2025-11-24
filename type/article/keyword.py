from pydantic import BaseModel


class Keyword(BaseModel):
    """Data Model for a Keyword Instance"""

    word: str
    score: float
