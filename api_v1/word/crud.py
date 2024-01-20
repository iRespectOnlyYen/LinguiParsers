from loguru import logger
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database.models import Word, SenseImage, Example, Sense, HtmlExample, Alias, WordImage
from core.schemas.schemas import CoreSWord, CoreSSense


async def get_word_by_id(
    session: AsyncSession,
    word_id: int,
) -> Word | None:
    return await session.get(Word, word_id)


async def get_word(
    session: AsyncSession,
    word: str,
) -> Word | None:
    stmt = select(Word).where(Word.word == word)
    return await session.scalar(stmt)


async def get_word_by_alias(
    session: AsyncSession,
    alias: str,
) -> Word | None:
    stmt = select(Alias).where(Alias.alias == alias.lower()).options(selectinload(Alias.word))
    if db_alias := await session.scalar(stmt):
        return db_alias.word


def get_db_examples_from_s_sense(sense: CoreSSense) -> list[Example]:
    db_examples = []
    for example in sense.examples:
        db_examples.append(Example(example=example))
    return db_examples


def get_db_html_examples_from_s_sense(sense: CoreSSense) -> list[HtmlExample]:
    db_html_examples = []
    for html_example in sense.html_examples:
        db_html_examples.append(HtmlExample(html_example=html_example))
    return db_html_examples


def get_db_word_images_from_s_public_word(word: CoreSWord) -> list[WordImage]:
    db_sense_images = []
    for img in word.images:
        db_sense_images.append(WordImage(img=img, is_public=True))
    return db_sense_images


def get_db_senses_from_s_public_word(word: CoreSWord) -> list[Sense]:
    senses = []
    for sense in word.senses:
        db_sense = Sense(
            lvl=sense.lvl,
            is_public=True,
            part_of_speech=sense.part_of_speech,
            definition=sense.definition,
            short_cut=sense.short_cut,
            examples=get_db_examples_from_s_sense(sense),
            html_examples=get_db_html_examples_from_s_sense(sense),
        )
        senses.append(db_sense)
    return senses


async def create_db_word(session: AsyncSession, word: CoreSWord, is_public: bool) -> Word:
    db_word = Word(word=word.word)
    db_word.aliases = [Alias(alias=word.alias)]
    if is_public:
        db_word.senses = get_db_senses_from_s_public_word(word)
    else:
        raise NotImplemented("Not implemented yet")
    db_word.sound_uk = word.sound_uk
    db_word.sound_us = word.sound_us
    db_word.word_images = get_db_word_images_from_s_public_word(word)
    session.add(db_word)
    await session.commit()
    return db_word


async def find_public_db_sense_by_definition(
    session: AsyncSession,
    definition: str,
) -> Sense | None:
    stmt = select(Sense).where(Sense.definition == definition).where(Sense.is_public)
    return await session.scalar(stmt)


async def create_or_supplement_db_public_word(
    session: AsyncSession,
    word: CoreSWord,
) -> Word:
    """метод для создания или дополнения контентом паблик слов"""
    db_word: Word = await get_word_by_alias(session, word.alias)
    if not db_word:
        db_word = await get_word(session, word.word)
        if db_word:
            db_alias = Alias(alias=word.alias.lower(), word=db_word)
            session.add(db_alias)

    if not db_word:
        return await create_db_word(session, word, is_public=True)

    db_senses: list[Sense] = get_db_senses_from_s_public_word(word)
    for db_sense in db_senses:
        if not await find_public_db_sense_by_definition(session, db_sense.definition):
            db_sense.word_id = db_word.id
            session.add(db_sense)

    await session.commit()
    return db_word


# async def get_all_word_data(session: AsyncSession, alias: str):
#     stmt = (
#         select(Alias)
#         .where(Alias.alias == alias)
#         .options(joinedload(Alias.word).selectinload(Word.senses).selectinload(Sense.examples))
#         .options(joinedload(Alias.word).selectinload(Word.senses).selectinload(Sense.row_examples))
#         .options(joinedload(Alias.word).selectinload(Word.senses).selectinload(Sense.images))
#     )
#     db_response = await session.execute(stmt)
#     result = db_response.scalar()
#     if result:
#         return WordDTO.model_validate(result.word)
#
#
# async def add_alias_to_word(session: AsyncSession, alias: str, word: str) -> Alias | None:
#     stmt = select(Alias).where(Alias.alias == alias)
#     db_alias = await session.scalar(stmt)
#     db_word = await get_word_by_name(session, word)
#     if not db_word:
#         return
#     if not db_alias:
#         db_alias = Alias(alias=alias, word=db_word)
#         session.add(db_alias)
#         await session.commit()
#         return db_alias
#
#
# def _filter_images_for_sense(sense: SenseDTO, collection: Iterable[int]) -> SenseDTO:
#     collection = set(collection)
#     sense = sense.model_copy()
#     sense.images = [img for img in sense.images if img.id in collection]
#     return sense
#
#
# async def get_sense_with_word_and_images_by_sense_id(
#     session: AsyncSession, sense_id: int, images_id: list[int] = None
# ) -> SenseDTO | None:
#     start = time.time()
#     stmt = (
#         select(Sense)
#         .options(
#             selectinload(Sense.images),
#             selectinload(Sense.examples),
#             selectinload(Sense.row_examples),
#             selectinload(Sense.word),
#         )
#         .where(Sense.id == sense_id)
#     )
#
#     sense_db = await session.scalar(stmt)
#     if sense_db:
#         logger.info(f"Time for get only one sense with images and example: {time.time()-start}s")
#         sense_dto = SenseDTO.model_validate(sense_db)
#         logger.info(f"Time for get only one sense with images and example: {time.time()-start}s")
#         return _filter_images_for_sense(sense_dto, images_id)
#
#
# async def get_many_senses_with_word_and_images_by_sense_id(
#     session: AsyncSession, senses_id: list[int], images_id: list[int] = None
# ) -> list[SenseDTO] | None:
#     stmt = (
#         select(Sense)
#         .options(
#             joinedload(Sense.images),
#             joinedload(Sense.examples),
#             joinedload(Sense.row_examples),
#             joinedload(Sense.word),
#         )
#         .filter(Sense.id.in_(senses_id))
#     )
#
#     row_response = await session.execute(stmt)
#     senses_db = row_response.scalars().unique().all()
#     if senses_db:
#         senses_dto: list[SenseDTO] = []
#         for sense in senses_db:
#             sense_dto = SenseDTO.model_validate(sense)
#             sense_dto_with_filtered_images = _filter_images_for_sense(sense_dto, images_id)
#             senses_dto.append(sense_dto_with_filtered_images)
#         return senses_dto
#
#
# async def get_image_by_id(session: AsyncSession, image_id: int) -> ImageDTO | None:
#     image_db = await session.get(Image, image_id)
#     if image_db:
#         return ImageDTO.model_validate(image_db)
