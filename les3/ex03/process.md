- чисто библиотеками requests и bs не получается сделать заопрос.
Возможно, блокируется получение информации, т.к. нет эмуляции пользователя
- попытка установить selenium для имитации захода с браузера(информация в куки и локал сторендж)
не получилось, нет chrome_driver (скорее слишком большой сайт для ответа)
лучше не использовать эту библиотеку, т.к. она больше подходит для имуляции поведения пользователя.
совершать клик и прочее
- использование requests_html


для запуска нужно:
- создать среду venv
- установить зависимости pip install -r requirements.txt
- запуск python3 financial.py 'MSFT' 'Total Revenue'


здесь использован пример с selenium

```
import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from requests_html import HTMLSession
import time


class Parser:
    def __init__(self, headless=True):
        # chrome_options = Options()
        # if headless:
        #     chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument(
        #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        # service = Service(ChromeDriverManager().install())

        # self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.session = HTMLSession()
        # print("✅ Chrome driver started")


    def request(self, url, param=None):
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        response.raise_for_status() # нужно для обработки ошибок - выбрасывает исключения
        page = BeautifulSoup(response.text, 'html.parser')

        print(page)

    # def request_for_selenium(self, url, wait_time=5):
    #     self.driver.get(url)
    #     time.sleep(wait_time)  # ждать пока загрузится JS

    #     soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    #     return soup
    
    def request_with_js(self, url, wait=3):
        """
        Загружает страницу и выполняет JavaScript
        """
        response = self.session.get(url)
        response.html.render(timeout=20, sleep=wait)  # запускаем JS, sleep — время ожидания в секундах
        return response.html

    def close(self):
        # self.driver.quit()
        self.session.close()
    

if __name__ == '__main__':
    parser = Parser()

    html = parser.request_with_js('https://finance.yahoo.com/quote/MSFT/financials/')
    print(html.text)
    print(html.find('title', first=True).text)
    # soup = parser.request_for_selenium('https://finance.yahoo.com/quote/MSFT/financials/')
    # soup = parser.request('https://timeweb.cloud/tutorials/python/kak-parsit-dannye-s-python')
    # soup = parser.request('https://finance.yahoo.com/quote/MSFT/financials/')
    # print(soup)
    

    parser.close()
    pass
```