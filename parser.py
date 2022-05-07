import time
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from tools.tools import SELECTOR_DICT, get_price, format_text
from work_excel_file import get_link_market, find_last_row_excel, set_price_to_book


headers = requests.utils.default_headers()
headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'})


async def get_page_data(session, url, cell, key_selector, copy_file):
    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'})
    async with session.get(url=url, headers=headers, timeout=30, allow_redirects=False) as response:
        try:
            selector = SELECTOR_DICT.get(key_selector)

            if response.status == 404:
                set_price_to_book(address=cell, price='http code 404', file_path=copy_file)

            if response is None:
                set_price_to_book(address=cell, price='Товар ожидается', file_path=copy_file)
            response_text = await response.text()

            text = get_price(response_text, key_selector)

            if not text:
                soup = BeautifulSoup(response_text, "lxml")
                elem = soup.select(selector=selector)
                text = elem[0].text

            text = format_text(text)
            set_price_to_book(address=cell, price=text, file_path=copy_file)

        except Exception as e:
            set_price_to_book(address=cell, price='Сервер недоступен', file_path=copy_file)
            print(e)


async def parser(original_file, copy_file):

    number_of_iterations, last_row = find_last_row_excel(original_file)

    generator = get_link_market(last_row=last_row, file_path=original_file)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for step in range(2, 500):
            print(step)
            url, cell, key_selector = next(generator)

            if url is None:
                continue

            # selector = SELECTOR_DICT.get(key_selector)

            task = asyncio.create_task(get_page_data(session, url, cell, key_selector, copy_file))

            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(parser('file/1.xlsx', 'file/2.xlsx'))

