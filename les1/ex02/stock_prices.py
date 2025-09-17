
import sys
# sys позволяет получить доступ к аргументам, если скрипт запускается из компандной строки
# sys.argv - list всех переменных под 0 индексом имя самого скрипта stock_prices.py
# python3 stock_prices.py apple good -> ['stock_prices.py', 'apple', 'good']
# полезные функции ещё (лишь часть): sys.exit([код]) - завершает программу с указынным кодом (по умолчанию 0)
#                                   sys.platform	Строка, указывающая платформу (например, 'win32', 'linux', 'darwin').
def print_price_action_company(key):
  COMPANIES = {
  'Apple': 'AAPL',
  'Microsoft': 'MSFT',
  'Netflix': 'NFLX',
  'Tesla': 'TSLA',
  'Nokia': 'NOK'
  }

  STOCKS = {
  'AAPL': 287.73,
  'MSFT': 173.79,
  'NFLX': 416.90,
  'TSLA': 724.88,
  'NOK': 3.37
  }

  key_company = get_value_with_key(COMPANIES, key)
  if not(key_company): 
    print('Unknown company')
    return

  value_action = get_value_with_key(STOCKS, key_company)

  if not(value_action):
    print('Отсутвует компания в списке акций')
    return
  
  print(value_action)

def get_value_with_key(obj, key):
  key_lower_case = key.lower()

  for k,v in obj.items():
    if k.lower() == key_lower_case: return v
  
  return False

# второй способ. пересоздавать списки с ключами в нижнем регистре
# и искать по переданному ключу переведя в нижний
# print(create_dict_with_low_case(COMPANIES)[key.lower()])
def create_dict_with_low_case(dict):
  return {k.lower(): v for k,v in dict.items()}

if __name__ == '__main__':
  if len(sys.argv) != 2 : 
    # print('Введите ключ для поиска')
    sys.exit(0)
  print_price_action_company(sys.argv[1])