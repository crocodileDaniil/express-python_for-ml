#!/usr/bin/env python3

import datetime
from collections import defaultdict, Counter
import pytest
import json
import re
import requests
from bs4 import BeautifulSoup
import os
import sys
from urllib.parse import urljoin
from functools import lru_cache

class Ratings:
    """
    Класс Ratings анализирует данные из файла ratings.csv.
    """
    def __init__(self, path_to_the_file):
        """
        Инициализация объекта. Загружаем данные (до 1000 строк).
        """
        self.data = []
        self.movies_titles = {}  # Можно расширить при наличии movies.csv

        try:
            with open(path_to_the_file, encoding='utf-8') as f:
                headers = f.readline().strip().split(',')
                for i, line in enumerate(f):
                    if i >= 10000:
                        break
                    values = line.strip().split(',')
                    if len(values) != 4:
                        continue
                    userId, movieId, rating, timestamp = values
                    self.data.append({
                        'userId': int(userId),
                        'movieId': int(movieId),
                        'rating': float(rating),
                        'timestamp': int(timestamp)
                    })
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")

        self.movies = self.Movies(self.data)
        self.users = self.Users(self.data)
    
    def transform_to_list(self, obj):
        return [x[0] for x in obj.items()]
    
    def random_sort(self, obj):
        return sorted(obj, key=lambda x: hash(x) % 100)
    
    def print_value(self, value):
        print(value)

    class Movies:
        def __init__(self, data):
            self.data = data

        def dist_by_year(self):
            """Возвращает словарь: {год: количество рейтингов} по годам (по timestamp)"""
            years = Counter()
            for row in self.data:
                try:
                    year = datetime.datetime.fromtimestamp(row['timestamp']).year
                    years[year] += 1
                except Exception:
                    continue
            return dict(sorted(years.items()))

        def dist_by_rating(self):
            """Возвращает словарь: {оценка: количество таких оценок} в отсортированном порядке"""
            ratings = Counter()
            for row in self.data:
                try:
                    ratings[row['rating']] += 1
                except Exception:
                    continue
            return dict(sorted(ratings.items()))

        def top_by_num_of_ratings(self, n):
            """Топ-N фильмов по числу оценок (словарь: movieId -> кол-во оценок)"""
            movie_counts = Counter()
            for row in self.data:
                movie_counts[row['movieId']] += 1
            return dict(movie_counts.most_common(n))

        def top_by_ratings(self, n, metric='average'):
            """Топ-N фильмов по средней или медианной оценке. metric='average' или 'median'."""
            movie_ratings = defaultdict(list)
            for row in self.data:
                movie_ratings[row['movieId']].append(row['rating'])

            result = {}
            for movie, ratings in movie_ratings.items():
                try:
                    if metric == 'average':
                        score = sum(ratings) / len(ratings)
                    elif metric == 'median':
                        sorted_r = sorted(ratings)
                        mid = len(sorted_r) // 2
                        if len(sorted_r) % 2 == 0:
                            score = (sorted_r[mid - 1] + sorted_r[mid]) / 2
                        else:
                            score = sorted_r[mid]
                    else:
                        continue
                    result[movie] = round(score, 2)
                except Exception:
                    continue

            return dict(sorted(result.items(), key=lambda x: x[1], reverse=True)[:n])

        def top_controversial(self, n):
            """Топ-N фильмов с наибольшей дисперсией оценок (самые противоречивые фильмы)."""
            movie_ratings = defaultdict(list)
            for row in self.data:
                movie_ratings[row['movieId']].append(row['rating'])

            result = {}
            for movie, ratings in movie_ratings.items():
                if len(ratings) > 1:
                    try:
                        mean = sum(ratings) / len(ratings)
                        variance = sum((r - mean) ** 2 for r in ratings) / (len(ratings) - 1)
                        result[movie] = round(variance, 2)
                    except Exception:
                        continue
            return dict(sorted(result.items(), key=lambda x: x[1], reverse=True)[:n])

    class Users(Movies):
        def __init__(self, data):
            super().__init__(data)

        def dist_by_num_of_ratings(self):
            """Словарь: {userId: количество поставленных оценок}"""
            user_counts = Counter()
            for row in self.data:
                user_counts[row['userId']] += 1
            return dict(sorted(user_counts.items()))

        def dist_by_rating(self, metric='average'):
            """Словарь: {userId: средняя или медианная оценка пользователя}"""
            user_ratings = defaultdict(list)
            for row in self.data:
                user_ratings[row['userId']].append(row['rating'])

            result = {}
            for user, ratings in user_ratings.items():
                try:
                    if metric == 'average':
                        score = sum(ratings) / len(ratings)
                    elif metric == 'median':
                        sorted_r = sorted(ratings)
                        mid = len(sorted_r) // 2
                        if len(sorted_r) % 2 == 0:
                            score = (sorted_r[mid - 1] + sorted_r[mid]) / 2
                        else:
                            score = sorted_r[mid]
                    else:
                        continue
                    result[user] = round(score, 2)
                except Exception:
                    continue
            return dict(sorted(result.items()))

        def top_n_users_by_variance(self, n):
            """Топ-N пользователей с самой высокой дисперсией оценок"""
            user_ratings = defaultdict(list)
            for row in self.data:
                user_ratings[row['userId']].append(row['rating'])

            result = {}
            for user, ratings in user_ratings.items():
                if len(ratings) > 1:
                    try:
                        mean = sum(ratings) / len(ratings)
                        variance = sum((r - mean) ** 2 for r in ratings) / (len(ratings) - 1)
                        result[user] = round(variance, 2)
                    except Exception:
                        continue
            return dict(sorted(result.items(), key=lambda x: x[1], reverse=True)[:n])

class Tags:
    """
    Анализ тегов из CSV-файла со столбцом 'tag'.
    ...
    """

    # Ссылка на прямой CSV в вашем Google Drive
    CSV_URL = "https://drive.google.com/uc?export=download&id=1cSBbmUCR-2f23hGPyT3OIb6R3ffMCa4L"

    def __init__(self, path_to_csv):
        # Если путь — директория, скачиваем туда tags.csv
        self.download_csv('resources')
        # path_to_csv = os.path.join(path_to_csv, "tags.csv")

        self.tags_list = []
        self.tags = []
        self.tag_counts = {}

        with open(path_to_csv, "r", encoding="utf-8") as f:
            header_line = f.readline()
            if not header_line:
                raise ValueError("Пустой CSV-файл")
            headers = header_line.strip().split(",")

            for idx, line in enumerate(f, start=2):
                cols = line.rstrip("\n").split(",")
                if len(cols) != len(headers):
                    raise ValueError(f"Строка {idx}: columns != headers")
                row = dict(zip(headers, cols))
                self.tags_list.append(row)

                tag = row.get("tag")
                if tag is None:
                    raise ValueError("Отсутствует столбец 'tag'")
                tag_clean = tag.strip().lower()
                if not tag_clean:
                    continue

                self.tags.append(tag_clean)
                self.tag_counts[tag_clean] = self.tag_counts.get(tag_clean, 0) + 1

    def download_csv(self, target_dir: str):
        """
        Скачивает CSV по CSV_URL в target_dir/tags.csv.
        """
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, "tags.csv")
        if os.path.isfile(target_path):
            return  # уже есть

        resp = requests.get(Tags.CSV_URL, stream=True)
        resp.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    def most_words(self, n):
        """
        Топ-n тегов по числу слов. Уникальные теги.
        Возвращает dict {tag: число_слов}.
        """
        if not isinstance(n, int) or n < 0:
            raise ValueError("n должен быть неотрицательным целым")
        unique_tags = set(self.tags)
        word_counts = {t: len(t.split()) for t in unique_tags}
        sorted_tags = sorted(
            word_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )
        return dict(sorted_tags[:n])

    def longest(self, n):
        """
        Топ-n тегов по длине строки. Уникальные теги.
        Возвращает список тегов.
        """
        if not isinstance(n, int) or n < 0:
            raise ValueError("n должен быть неотрицательным целым")
        unique_tags = set(self.tags)
        sorted_tags = sorted(unique_tags, key=len, reverse=True)
        return sorted_tags[:n]

    def most_words_and_longest(self, n):
        """
        Пересечение тегов из most_words(n) и longest(n).
        Возвращает список тегов.
        """
        mw = set(self.most_words(n).keys())
        lg = set(self.longest(n))
        return list(mw & lg)

    def most_popular(self, n):
        """
        Топ-n тегов по частоте в tag_counts.
        Возвращает dict {tag: count}.
        """
        if not isinstance(n, int) or n < 0:
            raise ValueError("n должен быть неотрицательным целым")
        sorted_tags = sorted(
            self.tag_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )
        return dict(sorted_tags[:n])

    def tags_with(self, word):
        """
        Уникальные теги, содержащие слово как отдельное слово,
        без учёта регистра. Возвращает отсортированный список.
        """
        if not isinstance(word, str) or not word:
            raise ValueError("word должен быть непустой строкой")
        pattern = re.compile(r"\b" + re.escape(word) + r"\b",
                             re.IGNORECASE)
        found = {t for t in self.tags if pattern.search(t)}
        return sorted(found)

    def write_json(self, data, output_file):
        """
        Запись списка словарей в JSON.
        (метод «переносит» из прежнего класса File.write_json)
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def write_csv(self, data, output_file):
        """
        Запись списка словарей в CSV.
        Все словари должны иметь одинаковые ключи.
        (взято из прежнего File.write_csv)
        """
        if not data:
            open(output_file, "w", encoding="utf-8").close()
            return

        keys = list(data[0].keys())
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(",".join(keys) + "\n")
            for row in data:
                if set(row.keys()) != set(keys):
                    raise ValueError("Несовпадение ключей в строках")
                row_values = (str(row[k]) for k in keys)
                f.write(",".join(row_values) + "\n")


class Links:
    """
    Analyzing data from links.csv
    """

    def __init__(self,
                 path_to_the_file='./resources/links_test.csv',
                 list_of_movies=None,
                 list_of_fields=None):
        self.file_path = path_to_the_file
        self.header = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        # self.csv_header_list = ['movieId', 'Director', 'Budget',
        #                         'Cumulative Worldwide Gross', 'Runtime']
        # self.csv_heder_str = 'movieId,Director,Budget,Cumulative Worldwide Gross,Runtime, Name\n'

        self.list_of_movies = list_of_movies
        self.list_of_fields = list_of_fields if list_of_fields else [
            'movieId', 'Director', 'Budget', 'Gross', 'Runtime', 'Name'
        ]
        self.cache_file = './services_folder/imdb_cache.json'
        self.cache = self._load_cache() or {}  # для кэша

    def transform_to_list(self, obj):
        return [x[0] for x in obj.items()]
    
    def random_sort(self, obj):
        return sorted(obj, key=lambda x: hash(x) % 100)
    
    def print_value(self, value):
        print(value)

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
                # убрать начальные отступы и ковычки -> создать массив из столбцов файла
                parts = [part.strip().strip('"') for part in line.split(',')]

                # проверка на структуру и вхять 2ой элмент.
                if len(parts) >= 2:
                    movie_id = parts[1]  # imdbId is in the second column
                    yield f'https://www.imdb.com/title/tt{movie_id}/'

    def parse_imdb_page(self, soup, movie_id):
        """
        Parse IMDB page. Проверка на корректность данных на странице.
        Вернуть словарь data с информацией {director: director и т.д.}
        """
        movie_info = [movie_id]
        box_office = None  # нужно было для тестов
        director, budget, cumulative_world_gross, run_time, name = [
            None for i in range(5)
        ]  # если не задать значения, то появляются ошибки для логов
        try:
            # Director
            director = soup.find(attrs={
                'data-testid': 'title-cast'
            }).find(
                class_=
                'ipc-metadata-list ipc-metadata-list--dividers-all sc-cd7dc4b7-8 immMHv ipc-metadata-list--base'
            ).find(class_=
                   'ipc-metadata-list__item ipc-metadata-list__item--align-end'
                   ).find('div').text
            movie_info.append(director)
        except (AttributeError, IndexError):
            movie_info.append('N/A')

        box_office = None  # нужно было для тестов
        try:
            # Budget and Gross
            box_office = soup.find(attrs={
                'data-testid': 'BoxOffice'
            }).find('ul')
            budget = box_office.find(attrs={
                'data-testid': 'title-boxoffice-budget'
            }).find('div').text.split()[0][1:]
            movie_info.append(budget)
        except (AttributeError, IndexError):
            movie_info.append('N/A')

        try:
            cumulative_world_gross = box_office.find(
                attrs={
                    'data-testid': 'title-boxoffice-cumulativeworldwidegross'
                }).find('div').text.split()[0][1:]
            movie_info.append(cumulative_world_gross)
        except (AttributeError, IndexError):
            movie_info.append('N/A')

        try:
            # Runtime
            run_time = soup.find(attrs={
                'data-testid': 'TechSpecs'
            }).find(attrs={
                'data-testid': 'title-techspecs-section'
            }).find(attrs={
                'data-testid': 'title-techspec_runtime'
            }).find('div').text
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

        return data

    # можно передать список фильмов и список колонок для анализа

    def get_imdb(self, list_of_movies=None, list_of_fields=None):
        """
        The method returns a list of lists [movieId, field1, field2, field3, ...] 
        for the list of movies given as the argument (movieId). 
        Sort it by movieId descendingly.
        """

        imdb_info = []

        if list_of_fields is None:
            list_of_fields = self.list_of_fields
        list_of_fields = [field.lower() for field in list_of_fields]

        allowed_fields = [field.lower() for field in self.list_of_fields]
        field_filter = [
            field for field in list_of_fields if field in allowed_fields
        ]

        if not field_filter:
            print("not found correct field. Available fields are:")
            print(
                "movieId, Director, Budget, Cumulative Worldwide Gross, Runtime, Name"
            )
            sys.exit(1)

        if self.cache: ## Добавил harodonr
            for movie_id, movie_data in self.cache.items():
                # фильтр по списку movieId, если нужно
                if list_of_movies and movie_id not in list_of_movies:
                    continue

                row = []
                for fld in field_filter:
                    if fld == 'movieid':
                        row.append(str(movie_id))
                    else:
                        # movie_data ключи в lower: director, budget, gross, runtime, name
                        val = movie_data.get(fld, 'N/A')
                        row.append(str(val))
                imdb_info.append(row)

            imdb_info.sort(key=lambda x: int(x[0]), reverse=True)
            return imdb_info
        
        # # ✅ Используем данные из cache, если он есть
        # if self.cache:
        #     for movie_id, movie_data in self.cache.items():
        #         if list_of_movies and movie_id not in list_of_movies:
        #             continue

        #         filtered_data = [str(movie_data.get(field, 'N/A')) for field in field_filter]
        #         imdb_info.append(filtered_data)

        #     imdb_info.sort(key=lambda x: int(x[0]), reverse=True)
        #     return imdb_info

        # ✅ Старое поведение: работать с URL, если cache пустой
        for url in self.imdb_url_generator():
            try:
                movie_id = url.split('/')[-2][2:]
                if list_of_movies and movie_id not in list_of_movies:
                    continue

                # response = requests.get(url, headers=self.header)
                response = self._fetch_url(url, headers=self.header) #не делаем запрос заново (harodonr)
                # response.raise_for_status()
                if not response:
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')

                full_movie_data = self.parse_imdb_page(soup, movie_id)

                filtered_data = [
                    str(full_movie_data.get(field, 'N/A'))
                    for field in field_filter
                ]
                imdb_info.append(filtered_data)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")
            except Exception as e:
                print(f"Error processing {url}: {e}")

        self._save_cache()
        imdb_info.sort(key=lambda x: int(x[0]), reverse=True)
        return imdb_info

    def format_time(self, time_str):
        """
        Format time string from IMDB to HH:MM format
        """
        hours = 0
        minutes = 0

        parts = time_str.split()
        # т.к. структура времени 1 hour 22 minutes -> [1,hour,22,minutes]
        for i in range(len(parts)):
            if parts[i] in ('hour', 'hours'):
                hours = int(parts[i - 1])
            elif parts[i] in ('minute', 'minutes'):
                minutes = int(parts[i - 1])

        return f"{hours}:{minutes:02d}"

    def top_directors(self, n=10):
        """
        The method returns a dict with top-n directors where the keys are directors and 
        the values are numbers of movies created by them. Sort it by numbers descendingly.
        """
        if n < 1: n = 1
        if not self.cache:
            self.get_imdb()

        directors = defaultdict(int)

        for movie_id in self.cache:
            director = self.cache[movie_id]['director']
            if director != 'N/A':
                directors[director] += 1

        sorted_directors = sorted(directors.items(),
                                  key=lambda x: x[1],
                                  reverse=True)

        return dict(sorted_directors[:n])

    def most_expensive(self, n: int):
        """
        Returns top-n movies by budget (descending).
        Keys: movie names, values: budgets as int.
        """
        if n < 1: n = 1

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
        if n < 1: n = 1

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
        if n < 1: n = 1

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
        if n < 1: n = 1

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

class Movies:
    """Analyzing data from movies.csv"""
    def __init__(self, path_to_the_file = './resources/movies(1000).csv'):
        """
        Put here any fields that you think you will need.
        """
        self.file_movies_path = path_to_the_file

    def transform_to_list(self, obj):
        return [x[0] for x in obj.items()]
    
    def random_sort(self, obj):
        return sorted(obj, key=lambda x: hash(x) % 100)
    
    def print_value(self, value):
        print(value)

    def get_columns(self, line):
        columns = ['']
        ch_sep = ','
        flag_new_column = False
        flag_quotes = False
        for ch in line:
            if ch == '\n': continue
            if ch == '"':
                flag_quotes = not flag_quotes
                continue

            if ch == ch_sep and not flag_quotes:
                flag_new_column = True
                continue

            if flag_new_column:
                columns.append('')
                flag_new_column = False

            columns[-1] += ch

        return columns

    def get_film_year(self, line):
        columns = self.get_columns(line)
        if len(columns) <3:
            print("Error Movies: incorrect structure file read")
        title = columns[1] # второй столбец это фильм
        border_left_year = title.rfind('(') + 1
        border_right_year = title.rfind(')')

        if border_left_year == -1 or border_right_year == -1:
            return None, None

        year = title[border_left_year:border_right_year]
        name = title[:border_left_year-1].strip()

        return name,year

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts. 
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        release_years = {}
        try:
            with open(self.file_movies_path, 'r') as file_movies:
                next(file_movies)

                for line in file_movies:
                    name,year = self.get_film_year(line)

                    if year is None: continue

                    if year in release_years:
                        release_years[year] += 1
                    else:
                        release_years[year] = 1

            sorted_release_years = dict(sorted(release_years.items(), key = lambda x: int(x[1]) ,reverse=True))
            return sorted_release_years
        except FileNotFoundError as e:
            print(e)
            sys.exit(2)
        except Exception as e:
            print(e)
            sys.exit(2)

    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
    Sort it by counts descendingly.
        """
        genres_counts = {}
        try:
            with open(self.file_movies_path, 'r') as file_movies:
                next(file_movies)

                for line in file_movies:
                    columns = self.get_columns(line)
                    if len(columns) != 3: continue

                    column_genres = columns[2] # 3я колонка жанры


                    if column_genres is None: continue

                    genres = column_genres.split('|')

                    for genr in genres:
                        if genr in genres_counts:
                            genres_counts[genr] += 1
                        else:
                            genres_counts[genr] = 1

            sorted_genres_counts = dict(sorted(genres_counts.items(), key = lambda x: int(x[1]) ,reverse=True))
            return sorted_genres_counts
        except FileNotFoundError as e:
            print(e)
            sys.exit(2)
        except Exception as e:
            print(e)
            sys.exit(2)

    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and 
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        movies = {}
        try:
            with open(self.file_movies_path, 'r') as file_movies:
                next(file_movies)

                for line in file_movies:
                    columns = self.get_columns(line)
                    if len(columns) != 3: continue

                    # 3я колонка жанры в вимде "A|B|C" и нам нужно кол-во
                    genres_count = len(columns[2].split('|'))
                    # беру с годом, т.к. так логичнее, поскольку могут быть одноиименные фильмы
                    film_name = columns[1]

                    movies[film_name] = genres_count
            sorted_movies = dict(sorted(movies.items(), key = lambda x: int(x[1]) ,reverse=True)[:n])

            return sorted_movies
        except FileNotFoundError as e:
            print(e)
            sys.exit(2)
        except Exception as e:
            print(e)
            sys.exit(2)

# ========== PYTEST ТЕСТЫ ========== #
class TestAll:
    @pytest.fixture
    def ratings(self):
        return Ratings("ratings.csv")

    def test_dist_by_year(self, ratings):
        result = ratings.movies.dist_by_year()
        assert all(isinstance(k, int) and isinstance(v, int) and v >= 1 for k, v in result.items())

    def test_dist_by_rating(self, ratings):
        result = ratings.movies.dist_by_rating()
        assert all(isinstance(k, float) and 0.5 <= k <= 5.0 and isinstance(v, int) and v >= 1 for k, v in result.items())

    def test_top_by_num_of_ratings(self, ratings):
        result = ratings.movies.top_by_num_of_ratings(5)
        values = list(result.values())
        assert isinstance(result, dict)
        assert all(isinstance(v, int) for v in values)
        assert values == sorted(values, reverse=True)

    def test_top_by_ratings_average(self, ratings):
        result = ratings.movies.top_by_ratings(5, metric='average')
        assert isinstance(result, dict)
        assert all(isinstance(v, float) for v in result.values())

    def test_top_by_ratings_median(self, ratings):
        result = ratings.movies.top_by_ratings(5, metric='median')
        assert isinstance(result, dict)
        assert all(isinstance(v, float) for v in result.values())

    def test_top_controversial(self, ratings):
        result = ratings.movies.top_controversial(5)
        assert isinstance(result, dict)
        assert all(isinstance(v, float) and v > 0 for v in result.values())

    def test_dist_by_num_of_ratings_users(self, ratings):
        result = ratings.users.dist_by_num_of_ratings()
        assert isinstance(result, dict)
        assert all(isinstance(k, int) and isinstance(v, int) and v >= 1 for k, v in result.items())

    def test_dist_by_rating_users(self, ratings):
        result = ratings.users.dist_by_rating('average')
        assert isinstance(result, dict)
        assert all(isinstance(v, float) for v in result.values())

    def test_top_n_users_by_variance(self, ratings):
        result = ratings.users.top_n_users_by_variance(5)
        assert isinstance(result, dict)
        assert all(isinstance(v, float) and v > 0 for v in result.values())

    @pytest.fixture
    def sample_csv(self, tmp_path):
        rows = [
            "userId,movieId,tag,timestamp",
            "1,10,foo bar,123",
            "2,20,hello,456",
            "3,30,test case,789",
            "4,40,foo bar,000",
        ]
        path = tmp_path / "tags.csv"
        path.write_text("\n".join(rows), encoding="utf-8")
        return str(path)

    @pytest.fixture(autouse=True)
    def setup_tags(self, sample_csv):
        self.tagger = Tags(sample_csv)

    def test_internal_storage(self):
        assert isinstance(self.tagger.tags_list, list)
        assert isinstance(self.tagger.tags, list)
        assert len(self.tagger.tags) == 4
        assert isinstance(self.tagger.tag_counts, dict)
        assert self.tagger.tag_counts["foo bar"] == 2

    def test_most_words(self):
        mw = self.tagger.most_words(2)
        assert isinstance(mw, dict)
        assert set(mw.keys()) <= {"foo bar", "test case"}
        vals = list(mw.values())
        assert vals == sorted(vals, reverse=True)

    def test_longest_tags(self):
        lg = self.tagger.longest(3)
        assert isinstance(lg, list)
        lengths = [len(tag) for tag in lg]
        assert lengths == sorted(lengths, reverse=True)
        assert len(set(lg)) == len(lg)

    def test_most_words_and_longest(self):
        both = self.tagger.most_words_and_longest(3)
        assert isinstance(both, list)
        assert set(both) == set(self.tagger.most_words(3)) & set(self.tagger.longest(3))

    def test_most_popular(self):
        mp = self.tagger.most_popular(1)
        assert isinstance(mp, dict)
        top_tag = list(mp.items())[0][0]
        assert top_tag == "foo bar"

    def test_tags_with(self):
        found = self.tagger.tags_with("hello")
        assert isinstance(found, list)
        assert found == ["hello"]
        assert self.tagger.tags_with("zzz") == []

    def test_errors_on_bad_args(self):
        with pytest.raises(ValueError):
            self.tagger.most_words(-1)
        with pytest.raises(ValueError):
            self.tagger.longest("3")
        with pytest.raises(ValueError):
            self.tagger.most_popular(None)
        with pytest.raises(ValueError):
            self.tagger.tags_with("")

    @pytest.fixture
    def sample_movies_csv(self, tmp_path):
        content = (
            "movieId,title,genres\n"
            "1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy\n"
            "2,Jumanji (1995),Adventure|Children|Fantasy\n"
            "3,Grumpier Old Men (1995),Comedy|Romance\n"
            "4,Waiting to Exhale (1995),Comedy|Drama|Romance\n"
            "5,Father of the Bride Part II (1995),Comedy\n"
        )
        file_path = tmp_path / "movies.csv"
        file_path.write_text(content, encoding="utf-8")
        return str(file_path)

    def test_dist_by_release(self, sample_movies_csv):
        movies = Movies(sample_movies_csv)
        result = movies.dist_by_release()
        assert isinstance(result, dict)
        assert result == {"1995": 5}

    def test_dist_by_genres(self, sample_movies_csv):
        movies = Movies(sample_movies_csv)
        result = movies.dist_by_genres()
        assert isinstance(result, dict)
        assert result.get("Comedy") == 4
        assert result.get("Romance") == 2
        assert "Animation" in result

    def test_most_genres(self, sample_movies_csv):
        movies = Movies(sample_movies_csv)
        result = movies.most_genres(3)
        assert isinstance(result, dict)
        assert "Toy Story (1995)" in result
        assert result["Toy Story (1995)"] == 5

    def test_invalid_path(self):
        with pytest.raises(SystemExit) as e:
            Movies("nonexistent_file.csv").dist_by_release()
        assert e.value.code == 2

    @pytest.fixture
    def links_with_mock_data(self):
        links = Links()
        links.cache = {
            "0114709": {"movieid": "0114709", "director": "Christopher Nolan", "budget": "$160,000,000", "gross": "$700,000,000", "runtime": "2:28", "name": "Inception"},
            "0113497": {"movieid": "0113497", "director": "Steven Spielberg", "budget": "$70,000,000", "gross": "$900,000,000", "runtime": "2:10", "name": "Jurassic Park"},
            "0113228": {"movieid": "0113228", "director": "Quentin Tarantino", "budget": "$8,000,000", "gross": "$200,000,000", "runtime": "2:34", "name": "Pulp Fiction"},
            "0113229": {"movieid": "0113228", "director": "Quentin Tarantino", "budget": "$8,000,000", "gross": "$200,000,000", "runtime": "2:30", "name": "Pulp"}
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
            assert isinstance(movies, int)


        # Проверка содержимого
        expected = {
            "Quentin Tarantino": ["0113228", "0113229"],  # 2 фильма
            "Christopher Nolan": ["0114709"]  # 1 фильм
        }
        assert len(result) == 2
        assert "Quentin Tarantino" in result
        assert result["Quentin Tarantino"] == 2
        assert "Christopher Nolan" in result
        assert result["Christopher Nolan"] == 1

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

# ========== РУЧНОЙ ЗАПУСК ВСЕХ МЕТОДОВ ========== #

if __name__ == "__main__":
    r = Ratings("ratings.csv")

    print("\nРаспределение по годам:")
    print(r.movies.dist_by_year())

    print("\nРаспределение по оценкам:")
    print(r.movies.dist_by_rating())

    print("\nТоп-5 фильмов по числу оценок:")
    print(r.movies.top_by_num_of_ratings(5))

    print("\nТоп-5 фильмов по средней оценке:")
    print(r.movies.top_by_ratings(5, metric='average'))

    print("\nТоп-5 фильмов по медианной оценке:")
    print(r.movies.top_by_ratings(5, metric='median'))

    print("\nТоп-5 самых противоречивых фильмов:")
    print(r.movies.top_controversial(5))

    print("\nРаспределение пользователей по числу оценок:")
    print(r.users.dist_by_num_of_ratings())

    print("\nСредняя оценка пользователей:")
    print(r.users.dist_by_rating(metric='average'))

    print("\nТоп-5 пользователей по дисперсии оценок:")
    print(r.users.top_n_users_by_variance(5))

    #Links
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
    sort_time = links_analyzer.longest(5)
    sort_cost_mitute = links_analyzer.top_cost_per_minute(5)
    print(result)
    print(sort_directors)
    print(sort_upper_money)
    print(sort_time)
    print(sort_cost_mitute)

    #Movies
    if len(sys.argv) > 2:
        print('Incorrect start program. Input file path')
        sys.exit(1)
        sys.exit(0)

    if len(sys.argv) == 2:
        movies = Movies(sys.argv[1])

        release_years = movies.dist_by_release()
        genres_sort = movies.dist_by_genres()
        sorted_movies = movies.most_genres(10)
        print(genres_sort)
        sys.exit(0)

    movies = Movies('./resources/movies(1000).csv')

    release_years = movies.dist_by_release()
    genres_sort = movies.dist_by_genres()
    sorted_movies = movies.most_genres(10)
    print(genres_sort)
