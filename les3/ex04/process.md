параметры запуска:
(1)

- python3 -m cProfile -s cumulative financial.py 'MSFT' 'Total Revenue' > profiling-sleeps.txt
  или
- python3 -m cProfile financial.py 'MSFT' 'Total Revenue' > profiling-sleep.txt

разница:
| -s cumulative | default |
| --- | --- |
| То же самое, но с флагом -s cumulative — сортировка по накопленному времени. | Просто запускает профилирование. |
| cumulative — это общее время, потраченное в функции и всех функциях, вызываемых ею. | По умолчанию сортирует вывод по времени внутреннего исполнения (time) функции. |
| Это удобно, если хочешь понять, какие крупные участки кода съедают всё время, даже если сама функция работает быстро, но вызывает "тяжёлые" вещи. | Это показывает, какие функции напрямую заняли больше всего времени. |

можно добавить для удобства мониторинга:

- pip install snakeviz
- python3 -m cProfile -o output.prof financial.py MSFT "Total Revenue"
- snakeviz output.prof
  (2)

- python3 -m cProfile -s cumulative financial.py 'MSFT' 'Total Revenue' > profiling-tottime.txt
  или
- python3 -m cProfile financial.py 'MSFT' 'Total Revenue' > profiling-tottime.txt

(3)

- python3 -m cProfile -o output.prof financial_enhanced.py MSFT "Total Revenue"
- python3 refactor_stat.py


нужно на будущее, парсинг через Playwright
| Возможность                    | `requests_html`        | `Playwright`                |
| ------------------------------ | ---------------------- | --------------------------- |
| Поддержка JavaScript           | Да (через Chromium)    | ✅ Полная и стабильная       |
| Поддержка асинхронности        | Нет                    | ✅ Да                        |
| Поддержка нескольких браузеров | Только Chromium        | ✅ Chromium, Firefox, WebKit |
| Поддержка эмуляции (моб./гео)  | Ограничена             | ✅ Да                        |
| Стабильность и скорость        | Средняя, иногда глючит | ✅ Надежный и быстрый        |


```
pip install playwright
playwright install
```

```
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


class PlaywrightParser:
    def __init__(self, ticker="MSFT"):
        self.ticker = ticker.upper()
        self.url = f"https://finance.yahoo.com/quote/{self.ticker}/financials?p={self.ticker}"

    def request_with_js(self, table_field: str):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # можно False, чтобы видеть окно
            page = browser.new_page()
            print(f'[Playwright] Navigating to: {self.url}')
            page.goto(self.url, timeout=30000)
            page.wait_for_selector(".tableBody", timeout=10000)  # дожидаемся таблицы

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")

        if not self.check_no_data(soup):
            return False

        data = self.get_data_field(soup, table_field)
        if not data:
            return

        data.insert(0, table_field)
        return tuple(data)

    def check_no_data(self, soup):
        try:
            no_data = soup.find(class_='noData yf-wnifss')
            if no_data and f"No results for '{self.ticker}'".lower() in no_data.text.lower():
                print(f'Not found data for ticker - {self.ticker}')
                return False
            return True
        except Exception as e:
            print(f'Check error: {e}')
            return True

    def get_data_field(self, soup, field):
        try:
            result = []
            rows = soup.find(class_='tableBody').find_all(class_='row')
            for row in rows:
                title = row.find(class_='rowTitle').text.strip().lower()
                if title == field.strip().lower():
                    cols = row.find_all(class_='column')[1:]
                    result = [c.text.strip() for c in cols]
                    return result
        except Exception as e:
            print(f'Field error: {e}')
        print("Field data not found")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py TICKER FIELD_NAME")
        sys.exit(1)

    parser = PlaywrightParser(sys.argv[1])
    result = parser.request_with_js(sys.argv[2])
    print(result)

```