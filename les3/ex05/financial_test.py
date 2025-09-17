import requests
from bs4 import BeautifulSoup
import sys
import time
import pytest
from unittest.mock import patch, Mock


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

    def request(self, table_field, url=None, param=None):
        if not url:
            url = self.initial_url
        print(f'url: {url}')
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            page = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP: {e}")
            return
        except Exception as e:
            print(f'Error in request: {e}')
            return

        if not page:
            print("Not page")
            return {
                "success": False,
                "body": "Not page"
            }

        is_check = self.check_no_data(page)
        if not is_check:
            return {
                "success": False,
                "body": f"Not found data is ticker - {self.ticker}"
            }

        data_in_field = self.get_data_field(page, table_field)

        if not data_in_field["success"]:
            return data_in_field

        data_in_field["body"].insert(0, table_field)
        result_response = tuple(data_in_field['body'])

        data_in_field["body"] = result_response

        return data_in_field

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
        try:
            table_rows = page.find(class_='tableBody').find_all(class_='row')
        except Exception as e:
            print(f"Error find table: {e}")
            return {"success": False,
                    "body": "Error find table"
                    }

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
            return {"success": False,
                    "body": "Field data not found"
                    }
        return {"success": True,
                "body": result
                }


def execute_the_program():
    if len(sys.argv) != 3:
        print("you need to specify a 'ticker' and a search 'field'")
        sys.exit(1)

    parser = Parser(sys.argv[1])
    data_field = parser.request(sys.argv[2])

    if not data_field["success"]:
        print(f"Error: {data_field['body']}")
        return data_field['body']
    print('sleep')
    time.sleep(5)
    print(data_field["body"])
    return data_field["body"]


if __name__ == '__main__':
    execute_the_program()

#  HTML success: True
sample_html_success = '''
<html>
  <body>
    <div class="tableBody">
      <div class="row">
        <div class="rowTitle column">Total Revenue</div>
        <div class="column">2021</div>
        <div class="column">2022</div>
        <div class="column">2023</div>
      </div>
    </div>
  </body>
</html>
'''

#  HTML success: True, на таблица изменена
sample_html_success_transform_table = '''
<html>
  <body>
    <div class="tableBodys">
      <div class="row">
        <div class="rowTitle column">Total Revenue</div>
        <div class="column">2021</div>
        <div class="column">2022</div>
        <div class="column">2023</div>
      </div>
    </div>
  </body>
</html>
'''

# HTML  success: False - "No results", если зашёл на страницу но нет данных для тикера
sample_html_no_data = '''
<html>
  <body>
    <div class="noData yf-wnifss">
      <div class="yf-wnifss">
        <p>No results for 'INVALID'</p>
      </div>
    </div>
  </body>
</html>
'''

# HTML success: False - no Data
sample_html_no_field = '''
<html>
  <body>
    <div class="tableBody">
      <div class="row">
        <div class="rowTitle">Operating Income</div>
        <div class="column">100</div>
      </div>
    </div>
  </body>
</html>
'''

# создание моковых данных для запроса
def mock_response(html, status_code=200):
    mock = Mock()
    mock.status_code = status_code
    mock.text = html
    return mock


@patch('requests.get')
def test_successful_request(mock_get):
    mock_get.return_value = mock_response(sample_html_success)
    parser = Parser("MSFT")
    result = parser.request("Total Revenue")
    assert result["success"] is True
    assert result["body"][0] == "Total Revenue"
    assert result["body"] == ("Total Revenue", "2021", "2022", "2023")
    assert isinstance(result["body"], tuple)
    assert len(result["body"]) == 4  

@patch('requests.get')
def test_successful_request_transform_table(mock_get):
    mock_get.return_value = mock_response(sample_html_success_transform_table)
    parser = Parser("MSFT")
    result = parser.request("Total Revenue")
    assert result["success"] is False
    assert result["body"] == "Error find table"


@patch('requests.get')
def test_invalid_ticker(mock_get):
    mock_get.return_value = mock_response(sample_html_no_data)
    parser = Parser("INVALID")
    result = parser.request("Total Revenue")
    assert result["success"] is False
    assert "Not found data is ticker" in result["body"]


@patch('requests.get')
def test_field_not_found(mock_get):
    mock_get.return_value = mock_response(sample_html_no_field)
    parser = Parser("MSSFT") # с ошыбочным тикером
    result = parser.request("Total Revenue")
    assert result["success"] is False
    assert result["body"] == "Field data not found"


@patch('requests.get')
def test_returns_tuple(mock_get):
    mock_get.return_value = mock_response(sample_html_success)
    parser = Parser("MSFT")
    result = parser.request("Total Revenue")
    assert isinstance(result["body"], tuple)

# функция обрабатывает верно, если перешла по неверному адресу
def test_check_no_data_returns_false():
    parser = Parser("INVALID")
    soup = BeautifulSoup(sample_html_no_data, "html.parser")
    assert parser.check_no_data(soup) is False

# функция обрабатывает верно, если перешла по верному адресу
def test_check_no_data_returns_true():
    parser = Parser("MSFT")
    soup = BeautifulSoup(sample_html_success, "html.parser")
    assert parser.check_no_data(soup) is True


def test_check_get_data_field_true():
    parser = Parser("MSFT")
    soup = BeautifulSoup(sample_html_success, "html.parser")
    field = parser.get_data_field(soup, "Total Revenue")
    assert field["success"] is True
    assert field["body"] == ["2021", "2022", "2023"]

def test_check_get_data_field_transform_table():
    parser = Parser("MSFT")
    soup = BeautifulSoup(sample_html_success_transform_table, "html.parser")
    field = parser.get_data_field(soup, "Total Revenue")
    assert field["success"] is False
    assert field["body"] == "Error find table"

def test_check_get_data_field_not_found():
    parser = Parser("MSFT")
    soup = BeautifulSoup(sample_html_success, "html.parser")
    field = parser.get_data_field(soup, "Total")
    assert field["success"] is False
    assert field["body"] == "Field data not found"


@patch('requests.get')
@patch('time.sleep')
def test_execute_success(sleep, mock_get, monkeypatch, capsys):
    #подмена sys.argv
    monkeypatch.setattr(sys, 'argv', ['parser_script.py', 'MSFT', 'Total Revenue'])
    
    mock_get.return_value = mock_response(sample_html_success)
    
    result = execute_the_program()

    assert isinstance(result, tuple)
    assert result[0] == "Total Revenue"
    assert result[1:] == ("2021", "2022", "2023")

    sleep.assert_called_once_with(5)
    # захват/перехват stdout (print)
    captured = capsys.readouterr()
    assert "sleep" in captured.out
    assert "Total Revenue" in captured.out

@patch('requests.get')
def test_execute_invalid_ticker(mock_get, monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['parser_script.py', 'INVALID', 'Total Revenue'])

    mock_get.return_value = mock_response(sample_html_no_data)

    result = execute_the_program()

    captured = capsys.readouterr()
    assert "Not found data is ticker" in captured.out
    assert "Error" in captured.out
    assert "Total Revenue" not in captured.out
    assert isinstance(result, str)

@patch('requests.get')
def test_execute_success(mock_get, monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['parser_script.py', 'MSFT', 'Total Revenue'])

    mock_get.return_value = mock_response(sample_html_success_transform_table)

    result = execute_the_program()

    assert isinstance(result, str)
    assert result == "Error find table"

    captured = capsys.readouterr()
    assert "Error" in captured.out