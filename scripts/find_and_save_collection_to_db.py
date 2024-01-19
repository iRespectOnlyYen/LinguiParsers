import asyncio
from typing import Iterable

import aiohttp
from loguru import logger
from aiohttp import TCPConnector
from aiohttp.client import ClientSession
from aiohttp.client import ClientTimeout

from core.database import db_helper
from core.schemas import CoreSWord
from api_v1.word import crud
from Parsers.main_collector import collect_and_download_one
from Parsers import SeleniumBaseImgCollector, GetImageLinksError
from fake_useragent import UserAgent


async def get_aiohttp_session():
    aiohttp_session_config: dict = {
        "headers": {"User-Agent": UserAgent.random},
        "connector": TCPConnector(force_close=True),
        "timeout": ClientTimeout(6 * 60 * 60),
    }
    return aiohttp.ClientSession(**aiohttp_session_config)


async def find_and_save_to_db(
    query: str,
    collector: SeleniumBaseImgCollector,
    aiohttp_session: ClientSession,
) -> None:
    try:
        core_word: CoreSWord = await collect_and_download_one(
            aiohttp_session, query=query, collector=collector
        )
    except GetImageLinksError:
        await asyncio.sleep(2)
        logger.error(query)
        core_word: CoreSWord = await collect_and_download_one(
            aiohttp_session, query=query, collector=collector
        )
    logger.info(core_word)
    async with db_helper.session_factory() as db_session:
        async with db_session.begin():
            await crud.create_or_supplement_db_public_word(db_session, core_word)


async def find_many_and_save_to_db(words: Iterable[str]) -> None:
    image_collector = SeleniumBaseImgCollector()
    with image_collector:
        async with await get_aiohttp_session() as aiohttp_session:
            for idx, word in enumerate(words, 1):
                logger.info((idx, word))
                try:
                    await find_and_save_to_db(word, image_collector, aiohttp_session)
                except Exception as Ex:
                    logger.error(Ex)
                    await asyncio.sleep(1)
                    await find_and_save_to_db(word, image_collector, aiohttp_session)
