# -*- coding: utf-8 -*-

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import requests
import re


class CianChecker(object):
    def __init__(self, spreadsheet_name, credentials_file):
        self.pattern_sold = r'Объявление снято с публикации'
        self.pattern_price = r'("offerPrice":)(\d{7,8}),'

        # get google authentication
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file,
                                                                       ['https://spreadsheets.google.com/feeds'])
        gc = gspread.authorize(credentials)
        # Open a worksheet from spreadsheet with one shot
        self.wks = gc.open(spreadsheet_name).sheet1

    def update_table(self):
        # find last column
        try:
            row = self.wks.row_values(1)
            new_col = row.index('') + 1
        except ValueError:
            self.wks.add_cols(1)
            row = self.wks.row_values(1)
            new_col = row.index('') + 1

        # write new date
        self.wks.update_cell(1, new_col, datetime.date.today())

        # find last row
        try:
            col = self.wks.col_values(1)
            last_row = col.index('') + 1
        except ValueError:
            self.wks.add_rows(1)
            col = self.wks.col_values(1)
            last_row = col.index('') + 1

        # update prices
        for row in range(2, last_row):
            url = self.wks.cell(row, 1).value
            self.wks.update_cell(row, new_col, str(self._get_price(url)))

    def _get_price(self, url):
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
            return re.search(self.pattern_price, web_page).group(2)
        except AttributeError:
            return 'N/A'


checker = CianChecker("cian", 'My Project-db502cd6c04d.json')
checker.update_table()

print('done')