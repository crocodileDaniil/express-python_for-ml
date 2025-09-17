- выдать права ```chmod +x benchmark.py```
- проверка существования питон ```ls /usr/bin/python3``` если нет, узнать  ```which python3 ```
- если не запускатеся скрипт, то проверить наличие Unix-концы строк, если он был сделан в windows, то содержит Windows (CRLF) 
```dos2unix benchmark.py``` 