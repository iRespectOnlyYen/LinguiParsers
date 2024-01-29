from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class SWordImage(BaseModel):
    img: str
    word_id: int = Field(exclude=True)
    is_public: bool
    id: int

    model_config = ConfigDict(from_attributes=True)


class WordModel(BaseModel):
    word: str
    sound_us: str
    sound_uk: str
    id: int


class HtmlExampleModel(BaseModel):
    html_example: str
    sense_id: int = Field(exclude=True)
    id: int


class SResponseSense(BaseModel):
    id: int
    short_cut: str | None = None
    part_of_speech: str | None = None
    word_id: int = Field(exclude=True)
    lvl: Literal["A1", "A2", "B1", "B2", "C1", "C2"] | None
    is_public: bool
    definition: str | None = None
    word_images: list[SWordImage] | None = []
    word: WordModel
    html_examples: list[HtmlExampleModel]

    model_config = ConfigDict(from_attributes=True)


class SResponseSenses(BaseModel):
    senses: list[SResponseSense]