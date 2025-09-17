import requests
from bs4 import BeautifulSoup
import os
import sys
from urllib.parse import urljoin
import json
from collections import defaultdict
from functools import lru_cache
import pytest

class Links:
    """
    Analyzing data from links.csv
    """

    def __init__(self, path_to_the_file='./resources/links_test.csv', list_of_movies=None, list_of_fields=None):
        self.file_path = path_to_the_file
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.csv_header_list = ['movieId', 'Director', 'Budget',
                                'Cumulative Worldwide Gross', 'Runtime']
        self.csv_heder_str = 'movieId,Director,Budget,Cumulative Worldwide Gross,Runtime, Name\n'

        self.list_of_movies = list_of_movies
        self.list_of_fields = list_of_fields if list_of_fields else [
            'movieId', 'Director', 'Budget', 'Gross', 'Runtime', 'Name']
        self.cache_file = './services_folder/imdb_cache.json'
        self.cache = self._load_cache() or {}  # для кэша

    def _load_cache(self):
       # _ соглашение для внутренних классов
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as cache_f:
                    return json.load(cache_f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_cache(self):
        # сохранение кэша на локальную машину
        # создать директорию, если нет
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

        with open(self.cache_file, 'w', encoding='utf-8') as cache_f:
            json.dump(self.cache, cache_f, ensure_ascii=False, indent=2)

    @lru_cache(maxsize=2000)  # память для кэша в url
    def _fetch_url(self, url):
        try:
            response = requests.get(url, headers=self.header, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}", file=sys.stderr)
            return None

    def imdb_url_generator(self, file_path=None):
        """
        генератор url адресов(надеюсь полезно будет для последующих)
        """
        path = file_path if file_path else self.file_path

        with open(path, 'r') as file:
            # пропуск шапки
            next(file)

            for line in file:
                # Split line by commas and strip whitespace/quotes
                parts = [part.strip().strip('"') for part in line.split(',')]

                # Ensure we have at least 2 columns (movieId and imdbId)
                if len(parts) >= 2:
                    movie_id = parts[1]  # imdbId is in the second column
                    yield f'https://www.imdb.com/title/tt{movie_id}/'

    def parse_imdb_page(self, soup, movie_id):
        """
        Parse IMDB page and extract required information
        Returns a list with movie info
        """
        movie_info = [movie_id]
        box_office = None  # нужно было для тестов
        director, budget, cumulative_world_gross, run_time, name = [
            None for i in range(5)]  # если не задать значения, то появляются ошибки для логов
        try:
            # Director
            director = soup.find(
                attrs={'data-testid': 'title-cast'}).find(class_='ipc-metadata-list ipc-metadata-list--dividers-all sc-cd7dc4b7-8 immMHv ipc-metadata-list--base').find(class_='ipc-metadata-list__item ipc-metadata-list__item--align-end').find('div').text
            movie_info.append(director)
        except (AttributeError, IndexError):
            movie_info.append('N/A')

        box_office = None  # нужно было для тестов
        try:
            # Budget and Gross
            box_office = soup.find(
                attrs={'data-testid': 'BoxOffice'}).find('ul')
            budget = box_office.find(
                attrs={'data-testid': 'title-boxoffice-budget'}).find('div').text.split()[0][1:]
            movie_info.append(budget)
        except (AttributeError, IndexError):
            movie_info.append('N/A')

        try:
            cumulative_world_gross = box_office.find(
                attrs={'data-testid': 'title-boxoffice-cumulativeworldwidegross'}).find('div').text.split()[0][1:]
            movie_info.append(cumulative_world_gross)
        except (AttributeError, IndexError):
            movie_info.append('N/A')

        try:
            # Runtime
            run_time = soup.find(attrs={'data-testid': 'TechSpecs'}).find(
                attrs={'data-testid': 'title-techspecs-section'}).find(
                attrs={'data-testid': 'title-techspec_runtime'}).find('div').text
            run_time = self.format_time(run_time)
            movie_info.append(run_time)
        except (AttributeError, IndexError):
            movie_info.append('N/A')

        try:
            # Name
            name = soup.find(attrs={'data-testid': 'hero__pageTitle'}).text
            movie_info.append(name)
        except (AttributeError, IndexError):
            movie_info.append('N/A')
        # благодаря тестам найдено, что нужно писать N/A
        data = {
            'movieid': movie_id,
            'director': director or 'N/A',
            'budget': budget or 'N/A',
            'gross': cumulative_world_gross or 'N/A',
            'runtime': run_time or 'N/A',
            'name': name or 'N/A'
        }

        self.cache[movie_id] = data

        # return movie_info
        return data
    # можно передать список фильмов и список колонок для анализа

    def get_imdb(self, list_of_movies=None, list_of_fields=None):
        """
        The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values should be parsed from the IMDB webpages of the movies.
        Sort it by movieId descendingly.
        """
        imdb_info = []

        if list_of_fields is None:
            list_of_fields = self.list_of_fields
            list_of_fields = [field.lower() for field in list_of_fields]
        else:
            # нижний регистр, для удобства
            list_of_fields = [field.lower() for field in list_of_fields]

        field_filter = []
        field_iterator = [field.lower() for field in self.list_of_fields]

        for field in list_of_fields:
            if field.lower() in field_iterator:
                field_filter.append(field.lower())

        # не нашёл ни одно поле
        if not field_filter:
            print("not found correct field. Plies print fields: ")
            print('movieId', 'Director', 'Budget',
                  'Cumulative Worldwide Gross', 'Runtime', 'Name')
            print('sep = ","')
            print(
                'example: ./links.py "./resources/links.csv" "0114709" "movieId,Director"')
            sys.exit(1)

        # Write to CSV file
        with open('imdb_infos.csv', 'w', newline='', encoding='utf-8') as csvfile:
            header_fields = []

            if not list_of_movies:
                list_of_movies = self.list_of_movies

            original_case = []

            for field_original in self.list_of_fields:
                if field_original.lower() in field_iterator:
                    original_case.append(field_original)

                header_fields = [*original_case]

            csvfile.write(','.join(header_fields) + '\n')

            for url in self.imdb_url_generator():
                try:
                    # получить id
                    movie_id = url.split('/')[-2][2:]

                    # Пропускает от
                    if list_of_movies and movie_id not in list_of_movies:
                        continue

                    response = requests.get(url, headers=self.header)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')

                    full_movie_data = self.parse_imdb_page(soup, movie_id)

                    filtered_data = [str(full_movie_data.get(field, 'N/A'))
                                     for field in field_filter]

                    imdb_info.append(filtered_data)
                    # Prepare CSV line (escape quotes and commas)
                    csv_stroke = []
                    for value in filtered_data:
                        # Экранируем специальные символы
                        escaped_value = str(value).replace('"', '""')
                        csv_stroke.append(f'"{escaped_value}"')

                    # строка csv файла
                    csvfile.write(','.join(csv_stroke) + '\n')

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching {url}: {e}")
                except Exception as e:
                    print(f"Error processing {url}: {e}")

        self._save_cache()
        # Sort by movieId descending
        imdb_info.sort(key=lambda x: int(x[0]), reverse=True)

        return imdb_info

    def format_time(self, time_str):
        """
        Format time string from IMDB to HH:MM format
        """
        hours = 0
        minutes = 0

        parts = time_str.split()

        for i in range(len(parts)):
            if parts[i] in ('hour', 'hours'):
                hours = int(parts[i-1])
            elif parts[i] in ('minute', 'minutes'):
                minutes = int(parts[i-1])

        return f"{hours}:{minutes:02d}"

    def top_directors(self, n=10):
        """
        The method returns a dict with top-n directors where the keys are directors and 
        the values are numbers of movies created by them. Sort it by numbers descendingly.
        """
        if not self.cache:
            self.get_imdb()
        directors = defaultdict(list)
        for movie_id in self.cache:
            director = self.cache[movie_id]['director']
            if director != 'N/A':
                directors[director].append(movie_id)

        sorted_directors = sorted(
            directors.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        return dict(sorted_directors[:n])

    def most_expensive(self, n: int):
        """
        Returns top-n movies by budget (descending).
        Keys: movie names, values: budgets as int.
        """
        if not self.cache:
            self.get_imdb()

        movies = []
        for movie_id, data in self.cache.items():
            budget_str = data.get('budget', 'N/A')
            if budget_str == 'N/A':
                continue

            try:
                budget = int(budget_str.replace('$', '').replace(',', ''))
                movies.append((data['name'], budget))
            except ValueError:
                continue

        movies.sort(key=lambda x: x[1], reverse=True)
        return dict(movies[:n])

    def most_profitable(self, n: int):
        """
        Returns top-n movies by profit (gross - budget).
        Keys: movie names, values: profit as int.
        """
        if not self.cache:
            self.get_imdb()

        profits = []
        for movie_id, data in self.cache.items():
            budget_str = data.get('budget', 'N/A')
            gross_str = data.get('gross', 'N/A')

            if 'N/A' in (budget_str, gross_str):
                continue

            try:
                budget = int(budget_str.replace('$', '').replace(',', ''))
                gross = int(gross_str.replace('$', '').replace(',', ''))
                profits.append((data['name'], gross - budget))
            except ValueError:
                continue

        profits.sort(key=lambda x: x[1], reverse=True)
        return dict(profits[:n])

    def longest(self, n: int):
        """
        Returns top-n longest movies.
        Keys: movie names, values: runtime strings.
        """
        if not self.cache:
            self.get_imdb()

        runtimes = []
        for movie_id, data in self.cache.items():
            runtime_str = data.get('runtime', 'N/A')
            if runtime_str == 'N/A':
                continue

            try:
                if ':' in runtime_str:
                    hours, minutes = map(int, runtime_str.split(':'))
                    total_mins = hours * 60 + minutes
                else:
                    total_mins = int(runtime_str)

                runtimes.append((data['name'], runtime_str, total_mins))
            except ValueError:
                continue

        runtimes.sort(key=lambda x: x[2], reverse=True)
        return {name: runtime for name, runtime, runtime_str in runtimes[:n]}

    def top_cost_per_minute(self, n: int):
        """
        Returns top-n movies by budget/minute.
        Keys: movie names, values: cost per minute (rounded to 2 decimals).
        """
        if not self.cache:
            self.get_imdb()

        costs = []
        for movie_id, data in self.cache.items():
            budget_str = data.get('budget', 'N/A')
            runtime_str = data.get('runtime', 'N/A')

            if 'N/A' in (budget_str, runtime_str):
                continue

            try:
                budget = float(budget_str.replace('$', '').replace(',', ''))

                if ':' in runtime_str:
                    hours, minutes = map(int, runtime_str.split(':'))
                    total_mins = hours * 60 + minutes
                else:
                    total_mins = float(runtime_str)

                if total_mins > 0:
                    cost = budget / total_mins
                    costs.append((data['name'], round(cost, 2)))
            except (ValueError, ZeroDivisionError):
                continue

        costs.sort(key=lambda x: x[1], reverse=True)
        return dict(costs[:n])


if __name__ == '__main__':
    if len(sys.argv) > 4:
        print("incorrect params")

    if len(sys.argv) == 4:
        list_of_movies = sys.argv[2].replace(' ', '').split(',')
        list_of_fields = sys.argv[3].replace(' ', '').split(',')
        links_analyzer = Links(sys.argv[1], list_of_movies, list_of_fields)
        # logick
        result = links_analyzer.get_imdb()
        print(result)
        sys.exit(0)

    if len(sys.argv) == 3:
        list_of_movies = sys.argv[2].replace(' ', '').split(',')
        links_analyzer = Links(sys.argv[1], list_of_movies)
        result = links_analyzer.get_imdb()
        print(result)
        sys.exit(0)

    if len(sys.argv) == 2:
        links_analyzer = Links(sys.argv[1])
        # logick
        result = links_analyzer.get_imdb()
        sort_directors = links_analyzer.top_directors(10)
        sort_budget = links_analyzer.most_expensive(10)
        sort_upper_money = links_analyzer.most_profitable(10)
        sort_time = links_analyzer.longest(5)
        sort_cost_mitute = links_analyzer.top_cost_per_minute(5)
        print(result)
        print(sort_directors)
        print(sort_upper_money)
        print(sort_time)
        print(sort_cost_mitute)
        sys.exit(0)

    links_analyzer = Links('./resources/links_test.csv')
    result = links_analyzer.get_imdb()
    sort_directors = links_analyzer.top_directors(10)
    sort_budget = links_analyzer.most_expensive(10)
    sort_upper_money = links_analyzer.most_profitable(10)
    sort_time = links_analyzer.longest(5,)
    sort_cost_mitute = links_analyzer.top_cost_per_minute(5)
    print(result)
    print(sort_directors)
    print(sort_upper_money)
    print(sort_time)
    print(sort_cost_mitute)

# можно убрать
result_imdb = [['0114709', 'John Lasseter', '30,000,000', '394,436,586', '1:21', 'История игрушек'], ['0113497', 'Joe Johnston', '65,000,000',
                                                                                                      '262,821,940', '1:44', 'Джуманджи'], ['0113228', 'Howard Deutch', '25,000,000', '71,518,503', '1:41', 'Старые ворчуны разбушевались']]
result_directors = {'John Lasseter': ['0114709'], 'Joe Johnston': [
    '0113497'], 'Howard Deutch': ['0113228']}
result_money = {'История игрушек': 364436586,
                'Джуманджи': 197821940, 'Старые ворчуны разбушевались': 46518503}
rrsult_time = {'Джуманджи': '1:44',
               'Старые ворчуны разбушевались': '1:41', 'История игрушек': '1:21'}
result_cost_minute = {'Джуманджи': 625000.0,
                      'История игрушек': 370370.37, 'Старые ворчуны разбушевались': 247524.75}


class TestLinks:
    """Тесты для класса Links с проверкой типов и сортировки"""

    @pytest.fixture
    def links_with_mock_data(self):
        """Фикстура с тестовыми данными"""
        links = Links()

        # Моковые данные, соответствующие структуре вашего кэша
        links.cache = {
            "0114709": {
                "movieid": "0114709",
                "director": "Christopher Nolan",
                "budget": "$160,000,000",
                "gross": "$700,000,000",
                "runtime": "2:28",
                "name": "Inception"
            },
            "0113497": {
                "movieid": "0113497",
                "director": "Steven Spielberg",
                "budget": "$70,000,000",
                "gross": "$900,000,000",
                "runtime": "2:10",
                "name": "Jurassic Park"
            },
            "0113228": {
                "movieid": "0113228",
                "director": "Quentin Tarantino",
                "budget": "$8,000,000",
                "gross": "$200,000,000",
                "runtime": "2:34",
                "name": "Pulp Fiction"
            },
            "0113229": {
                "movieid": "0113228",
                "director": "Quentin Tarantino",
                "budget": "$8,000,000",
                "gross": "$200,000,000",
                "runtime": "2:30",
                "name": "Pulp"
            }
        }
        links._save_cache()
        return links

    def test_get_imdb_types(self, links_with_mock_data):
        """Проверка типов данных, возвращаемых get_imdb()"""
        result = links_with_mock_data.get_imdb()

        assert isinstance(result, list)
        assert len(result) > 0

        for item in result:
            assert isinstance(item, list)
            assert len(item) == 6  # movieId + 5 полей

            # Проверка типов для каждого элемента
            assert isinstance(item[0], str)  # movieid
            assert isinstance(item[1], str)  # director
            assert isinstance(item[2], str)  # budget
            assert isinstance(item[3], str)  # gross
            assert isinstance(item[4], str)  # runtime
            assert isinstance(item[5], str)  # name

    def test_get_imdb_sorting(self, links_with_mock_data):
        """Проверка сортировки по movieId (descending)"""
        result = links_with_mock_data.get_imdb()
        print(result)
        # Извлекаем movieId из результатов
        movie_ids = [int(item[0]) for item in result]

        # Проверяем сортировку по убыванию
        assert all(movie_ids[i] >= movie_ids[i+1]
                   for i in range(len(movie_ids)-1))

    def test_top_directors(self, links_with_mock_data):
        """Проверка типов для top_directors()"""
        result = links_with_mock_data.top_directors(2)

        # Проверка типов
        assert isinstance(result, dict)

        assert isinstance(result, dict)
        for director, movies in result.items():
            assert isinstance(director, str)
            assert isinstance(movies, list)
            assert all(isinstance(movie, str) for movie in movies)

        # Проверка содержимого
        expected = {
            "Quentin Tarantino": ["0113228", "0113229"],  # 2 фильма
            "Christopher Nolan": ["0114709"]  # 1 фильм
        }
        assert len(result) == 2
        assert "Quentin Tarantino" in result
        assert len(result["Quentin Tarantino"]) == 2
        assert "Christopher Nolan" in result
        assert len(result["Christopher Nolan"]) == 1

    def test_most_expensive(self, links_with_mock_data):
        """Проверка типов для most_expensive()"""
        result = links_with_mock_data.most_expensive(2)

        assert isinstance(result, dict)
        for name, budget in result.items():
            assert isinstance(name, str)
            assert isinstance(budget, int)
        # Проверка преобразования бюджета
        assert result["Inception"] == 160000000
        assert result["Jurassic Park"] == 70000000

    def test_most_profitable(self, links_with_mock_data):
        """Проверка типов для most_profitable()"""
        result = links_with_mock_data.most_profitable(2)

        assert isinstance(result, dict)
        for name, profit in result.items():
            assert isinstance(name, str)
            assert isinstance(profit, int)
        # Проверка правильности расчета прибыли
        expected_profits = {
            "Jurassic Park": 900000000 - 70000000,
            "Inception": 700000000 - 160000000
        }

        assert result == expected_profits

    def test_longest(self, links_with_mock_data):
        """Проверка типов для longest()"""
        result = links_with_mock_data.longest(3)

        assert isinstance(result, dict)
        for name, runtime in result.items():
            assert isinstance(name, str)
            assert isinstance(runtime, str)
        # Проверка сортировки по времени
        expected_order = ["Pulp Fiction", "Pulp", "Inception"]
        assert list(result.keys()) == expected_order

        # Проверка значений времени
        assert result["Pulp Fiction"] == "2:34"
        assert result["Pulp"] == "2:30"
        assert result["Inception"] == "2:28"

    def test_top_cost_per_minute(self, links_with_mock_data):
        """Проверка типов для top_cost_per_minute()"""
        result = links_with_mock_data.top_cost_per_minute(2)

        assert isinstance(result, dict)
        for name, cost in result.items():
            assert isinstance(name, str)
            assert isinstance(cost, float)
        # Проверка расчета стоимости минуты
        inception_cost = 160000000 / (2*60 + 28)
        jumanji_cost = 70000000 / (2*60 + 10)

        expected_order = ["Inception", "Jurassic Park"]
        assert list(result.keys()) == expected_order

        # Проверка с округлением до 2 знаков
        assert round(result["Inception"], 2) == round(inception_cost, 2)
        assert round(result["Jurassic Park"], 2) == round(jumanji_cost, 2)

    @pytest.fixture
    def links_instance(self, tmp_path):
        """Фикстура с экземпляром Links и тестовым файлом кэша"""
        links = Links()
        links.cache_file = str(tmp_path / "test_cache.json")
        return links

    def test_load_cache_exists(self, links_instance, tmp_path):
        """Тест загрузки существующего кэша"""
        # Подготавливаем тестовый кэш
        test_data = {"0114709": {"name": "Inception"}}
        with open(links_instance.cache_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        # Проверяем загрузку
        result = links_instance._load_cache()
        assert result == test_data

    def test_load_cache_not_exists(self, links_instance):
        """Тест загрузки при отсутствии файла кэша"""
        assert not os.path.exists(links_instance.cache_file)
        result = links_instance._load_cache()
        assert result == {}

    def test_load_cache_invalid_json(self, links_instance, tmp_path):
        """Тест обработки поврежденного файла кэша"""
        with open(links_instance.cache_file, 'w', encoding='utf-8') as f:
            f.write("{invalid json}")

        result = links_instance._load_cache()
        assert result == {}

    def test_save_cache(self, links_instance, tmp_path):
        """Тест сохранения кэша"""
        test_data = {"0114709": {"name": "Inception"}}
        links_instance.cache = test_data

        links_instance._save_cache()

        assert os.path.exists(links_instance.cache_file)
        with open(links_instance.cache_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data

    def test_save_cache_creates_dir(self, links_instance, tmp_path):
        """Тест создания директории для кэша"""
        # Устанавливаем путь с несуществующей директорией
        links_instance.cache_file = str(tmp_path / "new_dir" / "cache.json")
        links_instance.cache = {"test": "data"}

        links_instance._save_cache()

        assert os.path.exists(links_instance.cache_file)

    def test_imdb_url_generator(self, links_instance, tmp_path):
        """Тест генератора URL IMDB"""
        # Создаем тестовый CSV файл
        test_csv = tmp_path / "test_links.csv"
        with open(test_csv, 'w', encoding='utf-8') as f:
            f.write('movieId,imdbId,tmdbId\n')
            f.write('1,0114709,862\n')
            f.write('2,0113497,8844\n')

        # Получаем генератор
        urls = links_instance.imdb_url_generator(str(test_csv))
        urls_list = list(urls)

        assert len(urls_list) == 2
        assert urls_list[0] == 'https://www.imdb.com/title/tt0114709/'
        assert urls_list[1] == 'https://www.imdb.com/title/tt0113497/'

    def test_parse_imdb_page(self, links_instance):
        """Тест парсинга страницы IMDB"""
        # Создаем тестовый HTML
        html = """
        <html>
            <div data-testid="hero__pageTitle">Test Movie</div>
            <div data-testid="title-cast">
                <div class="ipc-metadata-list ipc-metadata-list--dividers-all sc-cd7dc4b7-8 immMHv ipc-metadata-list--base">
                    <div class="ipc-metadata-list__item ipc-metadata-list__item--align-end">
                        <div>Test Director</div>
                    </div>
                </div>
            </div>
            <div data-testid="BoxOffice">
                <ul>
                    <li data-testid="title-boxoffice-budget">
                        <div>$100,000,000</div>
                    </li>
                    <li data-testid="title-boxoffice-cumulativeworldwidegross">
                        <div>$200,000,000</div>
                    </li>
                </ul>
            </div>
            <div data-testid="TechSpecs">
                <div data-testid="title-techspecs-section">
                    <div data-testid="title-techspec_runtime">
                        <div>2 hours 30 minutes </div>
                    </div>
                </div>
            </div>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Парсим страницу
        result = links_instance.parse_imdb_page(soup, "0114709")

        # Проверяем результат
        assert result == {
            'movieid': '0114709',
            'director': 'Test Director',
            'budget': '100,000,000',
            'gross': '200,000,000',
            'runtime': '2:30',
            'name': 'Test Movie'
        }
        assert links_instance.cache["0114709"] == result

    def test_parse_imdb_page_missing_data(self, links_instance):
        """Тест парсинга страницы с отсутствующими данными"""
        html = "<html><body>Invalid page</body></html>"
        soup = BeautifulSoup(html, 'html.parser')

        result = links_instance.parse_imdb_page(soup, "0114709")

        assert result == {
            'movieid': '0114709',
            'director': 'N/A',
            'budget': 'N/A',
            'gross': 'N/A',
            'runtime': 'N/A',
            'name': 'N/A'
        }
    def test_check_cache_content(links_with_mock_data):
        print(links_with_mock_data.cache)  # Посмотри, не пустой ли словарь
