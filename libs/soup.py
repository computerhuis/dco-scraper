import asyncio

import aiohttp
from bs4 import BeautifulSoup

from libs import configuration


async def load_url(url):
    if configuration.settings['debug']['soup']:
        print("Loading url: " + url)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()


def get_soup(url):
    text = asyncio.run(load_url(url))
    return BeautifulSoup(text.decode('utf-8'), 'html5lib')
