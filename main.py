import time
import requests
from bs4 import BeautifulSoup

from tools.tools import SELECTOR_DICT, get_price, format_text
from work_excel_file import get_link_market, find_last_row_excel, set_price_to_book

headers = requests.utils.default_headers()
headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'})


number_of_iterations, last_row = find_last_row_excel()

generator = get_link_market(last_row)
now = time.time()


for step in range(2, 200):
    try:

        url, cell, key_selector = next(generator)
        print(step)

        if url is None:
            continue
        selector = SELECTOR_DICT.get(key_selector)
        page = requests.get(url, headers=headers, timeout=15)

        if page.status_code == 404:
            set_price_to_book(address=cell, price='http code 404')
            continue
        if page is None:
            set_price_to_book(address=cell, price='Read timed out')

        text = get_price(page.text, key_selector)

        if not text:
            soup = BeautifulSoup(page.text, "lxml")
            elem = soup.select(selector=selector)
            text = elem[0].text

        text = format_text(text)
        set_price_to_book(address=cell, price=text)

    except Exception as e:
        set_price_to_book(address=cell, price='Товар ожидается')

        print(e)
print('====================================')
print(time.time() - now)