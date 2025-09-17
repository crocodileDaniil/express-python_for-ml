import urllib3
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import httpx
import sys

import cProfile


class Parser:
    base_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://finance.yahoo.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }

    def __init__(self, ticker="MSFT", header=base_header):
        self.headers = header
        self.ticker = ticker
        self.initial_url = f'https://finance.yahoo.com/quote/{ticker}/financials/?p={ticker.lower()}'
        self.http = urllib3.PoolManager()
        # если нужно переиспользование httpx и потом закрыть в close()
        # self.client = httpx.Client(headers=self.headers, follow_redirects=True)


    def request(self, table_field, url=None, param=None):
        if not url:
            url = self.initial_url
        print(f'url: {url}')
        try:
            response = self.http.request("GET", url, headers=self.headers)
            # time.sleep(5)
            # response.raise_for_status() # на этой не нужно
            page = BeautifulSoup(response.data, 'html.parser')
        except Exception as e:
            print(f'Error in request: {e}')
            return

        if not page:
            print("Not page")
            return

        is_check = self.check_no_data(page)
        if not is_check:
            return False

        data_in_field = self.get_data_field(page, table_field)

        if not data_in_field:
            return

        data_in_field.insert(0, table_field)
        result_response = tuple(data_in_field)

        # print(result_response)
        return result_response
    
    def request_httpx(self, table_field, url=None, param=None):
        if not url:
            url = self.initial_url
        print(f'url: {url}')
        try:
            # чтобы поток сам закрылся
            with httpx.Client(headers=self.headers, follow_redirects=True) as client:
                response = client.get(url)
                page = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f'Error: {e}')
            return

        if not page:
            print("Not page")
            return

        is_check = self.check_no_data(page)
        if not is_check:
            return False

        data_in_field = self.get_data_field(page, table_field)

        if not data_in_field:
            return

        data_in_field.insert(0, table_field)
        result_response = tuple(data_in_field)

        # print(result_response)
        return result_response

    def init_html_session(self):
        self.session = HTMLSession()
    # потом доработать на условный оператор

    def check_no_data(self, page):
        try:
            if page.find(class_='noData yf-wnifss').find(class_='yf-wnifss').find('p').text.lower() == f"No results for '{self.ticker}'".lower():
                print(f'Not found data is ticker - {self.ticker}')
                return False
            else:
                return True
        except Exception as e:
            print(f'Error check: {e}')
            return True

    def get_data_field(self, page, field):
        result = []
        field_not = True
        table_rows = page.find(class_='tableBody').find_all(class_='row')
        row_data = None

        for row in table_rows:
            title = row.find(class_='rowTitle').text.lower()
            if title == field.lower():
                data = row.find_all(class_='column')[1:]
                field_not = False
                for row in data:
                    result.append(row.text)
                break
        if field_not:
            print("Field data not found")
            return False
        return result
    # Загружает страницу и выполняет JavaScript

    def request_with_js(self, table_field, url=None, wait=2):
        if not url:
            url = self.initial_url
        print(f'[JS] url: {url}')

        try:
            if not hasattr(self, 'session'):
                self.init_html_session()

            response = self.session.get(url)
            response.html.render(timeout=20, sleep=wait)

            page = BeautifulSoup(response.html.html, 'html.parser')

        except Exception as e:
            print(f'Error in JS request: {e}')
            return

        if not page:
            print("Not page")
            return

        is_check = self.check_no_data(page)
        if not is_check:
            return False

        data_in_field = self.get_data_field(page, table_field)

        if not data_in_field:
            return

        data_in_field.insert(0, table_field)
        result_response = tuple(data_in_field)

        return result_response

    def close_session(self):
        self.session.close()


def execute_the_program():
    if len(sys.argv) != 3:
        print("you need to specify a 'ticker' and a search 'field'")
        sys.exit(1)

    parser = Parser(sys.argv[1])
    # data_field = parser.request(sys.argv[2])
    data_field = parser.request_httpx(sys.argv[2])
    print('end')
    # time.sleep(5)
    print(data_field)


if __name__ == '__main__':
    execute_the_program()
