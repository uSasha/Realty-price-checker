# -*- coding: utf-8 -*-

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

import datetime
import requests
import re


class CianChecker(object):
    def __init__(self, spreadsheet_name, credentials_file):
        self.sheet_name = spreadsheet_name
        self.credentials_file = credentials_file

    def update_table(self):
        # get google authentication
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file,
                                                                       ['https://spreadsheets.google.com/feeds'])
        gc = gspread.authorize(credentials)

        # Open a worksheet from spreadsheet with one shot
        wks = gc.open(self.sheet_name).sheet1

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
        wks.update_cell(1, new_col, datetime.date.today())

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
            wks.update_cell(i, new_col, str(self.get_price(wks, i)))

    def get_price(self, wks, row):
        url = wks.cell(row, 1).value
        marker = "Объявление снято с публикации"

        # check ad availability
        s = requests.session()
        try:
            result = s.get(url)
        except requests.exceptions.ConnectionError:
            return 'broken link'

        result = result.text
        match1 = re.findall(marker, result)    # we are trying to find marker in "result"
        if len(match1) == 1:
            return 'Sold'

        # get flat price
        try:
            pattern = r'("offerPrice":)(\d{7,8}),'
            match = re.search(pattern, result)
            return match.group(2)
        except AttributeError:
            return 'N/A'


checker = CianChecker("cian", 'My Project-db502cd6c04d.json')
checker.update_table()

print('done')