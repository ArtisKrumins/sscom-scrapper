# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuration variables
target_list = ['https://www.ss.com/lv/transport/cars/volkswagen/golf-7/sell/',
               'https://www.ss.com/lv/transport/cars/jaguar/all/sell/']
google_filename = "SS"
google_sheet_name = "cars"

# Process
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('data/creds.json', scope)
gc = gspread.authorize(credentials)
gc_file = gc.open(google_filename)
sheet = gc_file.worksheet(google_sheet_name)


def get_unique(worksheet):
    unique_list = []
    url_list = [item for item in worksheet.col_values(2) if item]
    date_list = [item for item in worksheet.col_values(4) if item]
    for k in range(len(url_list)):
        unique_item = date_list[k] + '|' + url_list[k]
        unique_list.append(unique_item)
    return unique_list


def col_names(worksheet):
    str_list = filter(None, worksheet.row_values(1))
    return str_list


def empty_row(worksheet):
    str_list = filter(None, worksheet.col_values(1))
    return str(len(str_list)+1)


def empty_col(worksheet):
    str_list = filter(None, worksheet.row_values(1))
    return str(len(str_list)+1)


def item_data(rows):
    results = {}
    for row in rows:
        aux = row.findAll('td')
        if aux[1].find('span') is not None:
            aux[1].span.decompose()
        if aux[0].find('img') is not None:
            aux[0].img.decompose()
        results[aux[0].string] = aux[1].get_text()
    return results


def get_listing(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/538.36'}
    html = None
    links = []
    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 200:
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            listing_section = soup.select('table > tr > td > a')
            for link in listing_section:
                cur_link = link['href'].strip()
                if '.html' in cur_link:
                    links.append(cur_link)
    except Exception as ex:
        print(str(ex))
    finally:
        return links


def parse(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/538.36'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        sleep(5)

        if r.status_code == 200:
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            for row in soup.find_all('td', {"class": "msg_footer"}):
                if 'Datums' in row.text.strip():
                    created = row.text.strip().replace('Datums: ', '')
            check = created + '|' + url

            if check not in current_records:
                # Pause for Google API request limit
                sleep(20)
                print("Processing new record " + check)
                next_row = empty_row(sheet)
                # Main data
                fetch_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sheet.update_acell('A' + next_row, fetch_time)
                sheet.update_acell('B' + next_row, url)
                price = soup.find('td', {"class": "ads_price"}).text.strip()
                sheet.update_acell('C' + next_row, "".join(_ for _ in price if _ in ".1234567890"))
                sheet.update_acell('D' + next_row, created)
                description = soup.find('div', {"id": "content_sys_div_msg"}).nextSibling.strip()
                sheet.update_acell('E' + next_row, description)

                # Dynamic data
                opt_table_1 = soup.find('table', {"class": "options_list"}).tr.td.table
                opt_table_2 = soup.find('table', {"class": "options_list"}).tr.td.nextSibling.table
                t1 = item_data(opt_table_1.findAll('tr'))
                t2 = item_data(opt_table_2.findAll('tr'))
                figures = t1.copy()
                figures.update(t2)
                print(figures)
                colons = col_names(sheet)
                for f in figures:
                    if f is not None:
                        figure_key = f.replace(':', '')
                    if figure_key in colons and figures[f] is not None:
                        # Add new records
                        sheet.update_cell(next_row, colons.index(figure_key)+1, figures[f])
                    elif figures[f] is not None:
                        # Add column and new record
                        next_col = empty_col(sheet)
                        sheet.update_cell(1, next_col, figure_key)
                        sheet.update_cell(next_row, next_col, figures[f])
            else:
                print("Skipping " + check)

    except Exception as ex:
        print(str(ex))
    finally:
            return "Success"


current_records = get_unique(sheet)
# Base run
for target in target_list:
    links = get_listing(target)
    [parse('https://www.ss.com' + link) for link in links]

