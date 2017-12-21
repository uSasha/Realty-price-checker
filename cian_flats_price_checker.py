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

        # get google authentication
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file,
                                                                       ['https://spreadsheets.google.com/feeds'])
        gc = gspread.authorize(credentials)

        # Open a worksheet from spreadsheet with one shot
        self.wks = gc.open(self.sheet_name).sheet1

        self.pattern_sold = r'Объявление снято с публикации'
        self.patter_price = r'("offerPrice":)(\d{7,8}),'
        self.pattern_captcha = r'captcha'

    def update_table(self):
        # find last column
        row = self.wks.row_values(1)
        try:
            new_col = row.index('')
        except ValueError:
            self.wks.add_cols(1)
            row = self.wks.row_values(1)
            new_col = row.index('')
        new_col += 1  # table starts from 1, but list starts from 0

        # write new date
        self.wks.update_cell(1, new_col, datetime.date.today())

        # find last raw
        col = self.wks.col_values(1)
        try:
            last_raw = col.index('')
        except ValueError:
            self.wks.add_rows(1)
            col = self.wks.col_values(1)
            last_raw = col.index('')
        last_raw += 1  # table starts from 1, but list starts from 0

        # update prices
        for i in range(2, last_raw):
            self.wks.update_cell(i, new_col, str(self.get_price(i)))

    def get_price(self, row):
        url = self.wks.cell(row, 1).value

        # check ad availability
        s = requests.session()
        try:
            web_page = s.get(url).text
        except requests.exceptions.ConnectionError:
            return 'Broken link'

        if re.search(self.pattern_sold, web_page):
            return 'Sold'

        # get flat price
        try:
            return re.search(self.patter_price, web_page).group(2)
        except AttributeError:
            return 'N/A'


checker = CianChecker("cian", 'My Project-db502cd6c04d.json')
checker.update_table()

print('done')