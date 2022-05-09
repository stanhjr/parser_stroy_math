import time
import io
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from tools.tools import SELECTOR_DICT, get_price, format_text
from work_excel_file import get_link_market, find_last_row_excel, set_price_to_book, get_all_link_market
import encodings

encodings.aliases.aliases['cp_1251'] = 'cp1251'

sema = asyncio.BoundedSemaphore(5)


async def get_page_data(session, url, cell, key_selector, copy_file):
    ua = UserAgent()
    try:
        print(cell)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': ua.random,
            "Cookie": 'ymex=1962878606.yrts.1647518606#1962878606.yrtsi.1647518606; yandexuid=7334774781647518606; yuidss=7334774781647518606; i=QKr00Nm/0UePVn1eR2akaV7LfpJPzm2XBoDpHkoz7rvA4S8ceQ+5edhvhD536K6bWxGSx9btEMzxYa4C0yl4wxKZ5VM=; is_gdpr=0; is_gdpr_b=CLfGQxD7aA==; yabs-sid=2459537251652003522',

        }
    except IndexError:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': ua.random
        }
    counter_404 = 0
    counter_except = 0
    counter_none = 0
    final = False
    for proxy in range(4):
        try:
            async with session.get(url=url, headers=headers, allow_redirects=True, timeout=30) as response:

                print('cell', cell, proxy)

                selector = SELECTOR_DICT.get(key_selector)

                if key_selector == 'I':
                    response_text = await response.text(encoding='ISO-8859-1')
                else:

                    html = await response.text()
                    buffer = io.BufferedReader(io.BytesIO(html.encode("utf-8")))
                    text_wrapper = io.TextIOWrapper(buffer)
                    response_text = text_wrapper.read()

                if response.status == 404:
                    set_price_to_book(address=cell, price='Страница не найдена', file_path=copy_file)
                    return

                if response is None:
                    set_price_to_book(address=cell, price='Товар ожидается', file_path=copy_file)
                    counter_none += 1
                    return
                if response_text:
                    text = get_price(response_text, key_selector)

                    if not text:
                        soup = BeautifulSoup(response_text, "lxml")
                        elem = soup.select(selector=selector)
                        text = elem[0].text

                    text = text.strip()
                    text = text.strip()
                    text = text.strip()
                    if key_selector == 'I':
                        text = bytes(text, 'iso-8859-1').decode('utf-8')
                    text = format_text(text)
                    set_price_to_book(address=cell, price=text, file_path=copy_file)
                    return

        except aiohttp.ServerDisconnectedError as e:
            print(e, cell, counter_except)
            counter_except += 1
            await asyncio.sleep(4)
            if counter_except == 3:
                set_price_to_book(address=cell, price='Сервер недоступен', file_path=copy_file)
            continue

        except IndexError:
            set_price_to_book(address=cell, price='Товар ожидается', file_path=copy_file)
            break

        except asyncio.TimeoutError as e:
            print(e, cell, counter_except)
            counter_except += 1
            await asyncio.sleep(4)
            if counter_except == 3:
                set_price_to_book(address=cell, price='Сервер недоступен', file_path=copy_file)
            continue


async def parser(copy_file, first_row, last_row, all_data):
    connector = aiohttp.TCPConnector(limit=5)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []

            for url, cell, key_selector in all_data[first_row:last_row]:
                if url is None:
                    continue
                task = asyncio.create_task(get_page_data(session, url, cell, key_selector, copy_file))
                tasks.append(task)

            await asyncio.gather(*tasks)
            return first_row, last_row
    except aiohttp.ServerDisconnectedError as e:
        print(e)


async def all_parsing(original_file, copy_file):
    number_of_iterations, last_row = await find_last_row_excel(file_path=original_file)
    all_data = get_all_link_market(last_row=last_row, file_path=original_file)
    first_row_row_in_one_parse = 0
    last_row_in_one_parse = 80
    number_of_run = number_of_iterations // last_row_in_one_parse

    if number_of_iterations % number_of_run != 0:
        number_of_run += 1

    for i in range(number_of_run):
        first_row_row_in_one_parse, last_row_in_one_parse = await parser(copy_file=copy_file,
                                                                         first_row=first_row_row_in_one_parse,
                                                                         last_row=last_row_in_one_parse,
                                                                         all_data=all_data)
        time.sleep(3)
        first_row_row_in_one_parse += 80
        last_row_in_one_parse += 80

    return copy_file
