import os
import shutil
import time
from openpyxl.reader import excel


# shutil.copy2('file/1.xlsx', 'file/2.xlsx')
#
# wb = excel.load_workbook('file/1.xlsx', read_only=False, keep_vba=False, data_only=False, keep_links=True)
# wb2 = excel.load_workbook('file/2.xlsx', read_only=False, keep_vba=False, data_only=False, keep_links=True)
# wb.active = 0
# sheet = wb.active


def set_price_to_book(address, price, file_path):
    try:
        wb = excel.load_workbook(file_path, read_only=False, keep_vba=False, data_only=False, keep_links=True)
        wb.active = 0
        sheet = wb.active
        sheet[address] = price
        wb.save(file_path)
        return True
    finally:
        wb.save(file_path)


def get_link_market(last_row: int, file_path):
    wb = excel.load_workbook(file_path, read_only=False, keep_vba=False, data_only=False, keep_links=True)
    wb.active = 0
    sheet = wb.active

    counter = 2
    row_excel_book = 'DEFGHIJKLMNOP'
    while counter != last_row:
        for liter in row_excel_book:
            yield sheet[liter + str(counter)].value, sheet[liter + str(counter)].coordinate, sheet[liter + str(counter)].coordinate[0]
        counter += 1


def find_last_row_excel(file_path):
    wb = excel.load_workbook(file_path, read_only=False, keep_vba=False, data_only=False, keep_links=True)
    wb.active = 0
    sheet = wb.active
    row_excel_book = 'DEFGHIJKLMNOP'
    row = 2
    while True:
        row += 1
        for cell_number in range(row, row + 1):
            counter = 0
            for liter in row_excel_book:
                if sheet[liter + str(cell_number)].value is None:
                    counter += 1
                if counter == len(row_excel_book):
                    return int(sheet[liter + str(cell_number)].coordinate[1:]) * len(row_excel_book), int(sheet[liter + str(cell_number)].coordinate[1:])















