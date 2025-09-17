| Аргумент      | Задача                                                 |
| ------------- | -------------------------------------------------------- |
| `monkeypatch` | Позволяет временно изменить `sys.argv`                   |
| `mock_get`    | Подменяет `requests.get`, возвращает HTML                |
| `capsys`      | Захватывает `print()` из `stdout`, можно проверить вывод |


### для тестов функции main

* mock_get — передаётся от @patch.

* monkeypatch — встроенная фикстура pytest, позволяет подменять поведение кода (в данном случае — sys.argv).

* capsys — тоже фикстура pytest, позволяет захватывать весь stdout/stderr (всё, что print()).

```
@patch('requests.get')
@patch('time.sleep')
def test_execute_success(sleep, mock_get, monkeypatch, capsys):
```
первые 2 фикстуры созданы мной и имена могут быть любые, которые используются в pytest менять нельзя.