# -*- coding: utf-8 -*-

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

import datetime
import requests
import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


def time_get():
    return str(datetime.date.today())


def get_price(wks, row):
    url = wks.cell(row, 1).value
    marker = "Объявление снято с публикации"

    # check ad availability
    s = requests.session()
    result = s.get(url)     # TODO check if it's there
    result = result.text
    match1 = re.findall(marker, result)    # we are trying to find marker in "result"
    if len(match1) == 1:
        return 'N/A'

    # get flat price
    only_tags_with_id_rur = SoupStrainer(id="price_rur")
    s = BeautifulSoup(result, "html.parser", parse_only=only_tags_with_id_rur).prettify()

    print('price:', s, 'here')
    return re.findall(r'\d+', s)[0]   # get first number from string


def check_cian():
    # get google authentication
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('My Project-db502cd6c04d.json', scope)

    gc = gspread.authorize(credentials)

    # Open a worksheet from spreadsheet with one shot
    wks = gc.open("cian").sheet1

    # find last column
    row = wks.row_values(1)
    try:
        new_col = row.index('')
    except ValueError:
        wks.add_cols(1)
        row = wks.row_values(1)
        new_col = row.index('')
    new_col += 1  # table starts from 1, but list starts from 0

    # write new date
    wks.update_cell(1, new_col, time_get())

    # find last raw
    col = wks.col_values(1)
    try:
        last_raw = col.index('')
    except ValueError:
        wks.add_rows(1)
        col = wks.col_values(1)
        last_raw = col.index('')
    last_raw += 1  # table starts from 1, but list starts from 0

    # update prices
    for i in range(2, last_raw):
        wks.update_cell(i, new_col, str(get_price(wks, i)))


check_cian()
print('done')