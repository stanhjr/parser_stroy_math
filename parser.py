import time
import io
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from tools.tools import SELECTOR_DICT, get_price, format_text
from work_excel_file import get_link_market, find_last_row_excel, set_price_to_book
import encodings

encodings.aliases.aliases['cp_1251'] = 'cp1251'

# headers = requests.utils.default_headers()
# headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'})
# headers.update({'Content-type': 'text/plain; charset=utf-8'})
sema = asyncio.BoundedSemaphore(5)


async def get_page_data(session, url, cell, key_selector, copy_file, step):

    ua = UserAgent()
    try:
        print(step)
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
    for i in range(4):
        try:
            async with session.get(url=url, headers=headers, allow_redirects=True) as response:


                print('cell', cell)

                selector = SELECTOR_DICT.get(key_selector)

                if key_selector == 'I':
                    response_text = await response.text(encoding='ISO-8859-1')
                else:

                    html = await response.text()
                    buffer = io.BufferedReader(io.BytesIO(html.encode("utf-8")))
                    textWrapper = io.TextIOWrapper(buffer)
                    response_text = textWrapper.read()

                if response.status == 404:
                    set_price_to_book(address=cell, price='http code 404', file_path=copy_file)
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
                    await asyncio.sleep(0.5)
                    return

        except aiohttp.ServerDisconnectedError as e:
            print(e, cell)
            counter_except += 1
            await asyncio.sleep(4)
            if counter_except == 3:
                set_price_to_book(address=cell, price='Сервер недоступен', file_path=copy_file)
            continue

        except IndexError:
            set_price_to_book(address=cell, price='Товар ожидается', file_path=copy_file)
            break

        except Exception as e:
            set_price_to_book(address=cell, price='Сервер недоступен', file_path=copy_file)
            counter_none += 1
            print(e)
            print(cell)
            break


async def sleep(seconds: int):
    await asyncio.sleep(seconds)


async def parser(original_file, copy_file):
    number_of_iterations, last_row = await find_last_row_excel(original_file)
    connector = aiohttp.TCPConnector(limit=1)
    generator = get_link_market(last_row=last_row, file_path=original_file)
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for step in range(2, 600):
                url, cell, key_selector = next(generator)

                if url is None:
                    continue

                task = asyncio.create_task(get_page_data(session, url, cell, key_selector, copy_file, step))
                # if step % 11 == 0:
                #     task2 = asyncio.create_task(sleep(4))
                #     tasks.append(task2)
                tasks.append(task)
            for step in range(601, 1200):
                url, cell, key_selector = next(generator)

                if url is None:
                    continue

                task = asyncio.create_task(get_page_data(session, url, cell, key_selector, copy_file, step))
                # if step % 11 == 0:
                #     task2 = asyncio.create_task(sleep(4))
                #     tasks.append(task2)
                tasks.append(task)

            await asyncio.gather(*tasks)
            return copy_file
    except aiohttp.ServerDisconnectedError as e:
        print(e)


if __name__ == '__main__':
    now = time.time()
    try:
        fff = asyncio.run(parser('file/1.xlsx', 'file/2.xlsx'))
    except aiohttp.ClientOSError as e:
        print(e)
    except aiohttp.ServerDisconnectedError as e:
        print(e)
        # asyncio.run(parser('file/1.xlsx', 'file/2.xlsx'))
    print(time.time() - now)
