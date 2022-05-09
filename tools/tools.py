from bs4 import BeautifulSoup


SELECTOR_DICT = {
    'D': '#prices > div > div > div.card-body.py-3.px-4 > dl > dd:nth-child(2)',
    'E': '#prices > div > div > div.card-body.py-3.px-4 > dl > dd:nth-child(4)',
    'F': '#content > div > div.col-md-5.col-sm-7.col-xs-6.col-50 > div.area-1 > div.price-block > ul > li:nth-child(2) > h2 > span.autocalc-product-special',
    'G': '#main > div.pc-product-single__summary-wrapper > div.pc-product-single__summary > div > div.pc-product-summary__body > div.pc-product-purchase > div.pc-product-purchase__header > div.product-price.product-price--lg > span',
    'H': '#main > div.pc-product-single__summary-wrapper > div.pc-product-single__summary > div > div.pc-product-summary__body > div.pc-product-purchase > div.pc-product-purchase__header > div.product-price--wholesale > div > span',
    'I': '#price',
    'J': '#price_base',
    'K': '#MAIN > div > div.p-block__row.p-block__row--price > div > div',
    'L': '#main-product-price',
    'M': '#fix_right_block > div.panel.panel-default.panel-body > div.price > span',
    'N': '#main > div.pc-product-single__summary-wrapper > div.pc-product-single__summary > div > div.pc-product-summary__body > div > div.pc-product-purchase__header > div > span',
    'O': 'body > main > article > div.cs-page__main-content > div.cs-product.js-productad > div.cs-product__info-row > div.cs-product__wholesale-price.cs-online-edit > div > p > span:nth-child(1)',
    'P': '#body_text > div.catalog-detail > table > tbody > tr > td:nth-child(2) > div.price_buy_detail > div.catalog-detail-price > span.catalog-detail-item-price',
}


def get_price(page_text, liter_key):
    elem = None
    soup = BeautifulSoup(page_text, "lxml")
    if liter_key == 'D':
        elem = soup.find('span', class_='product-cat-price-current')

    # if liter_key == 'E':
    #     elem = soup.find('span', class_='product-cat-price-current')

    if liter_key == 'P':
        elem = soup.find('span', class_='catalog-detail-item-price')

    if liter_key == 'F':
        elem = soup.find('span', class_='autocalc-product-price')

    if liter_key == 'N':
        elem = soup.find('span', class_='woocommerce-Price-amount amount')

    if elem:
        return elem.text


def format_text(text):
    text = text.replace(' ', '')
    for symbol in text:
        if symbol.isalpha() or symbol == '/':
            text = text.replace(symbol, '')
    if text[-1] == '.':
        text = text[:len(text) - 1]
    text = text.replace('.', ',')
    text = text.replace('\n', '')
    text = text.replace('\t', '')
    return text


async def edit_message(chat_id, msg_id, text):
    from bot import bot
    await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text)








