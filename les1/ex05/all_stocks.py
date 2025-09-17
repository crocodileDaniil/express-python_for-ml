import sys
def detect_ticker_or_company(elements):
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

  for element in elements:
    # Определяется поиск по компании, если передана компания, то
    # будет находиться list: ticker компании [0] и сама компания [1]  или False
    is_company = give_partner(COMPANIES, element.lower())
    # Определяется поиск по ticker, если передан ticker, то
    # будет находиться list: компания [0] и сам ticker [1]  или False 
    is_ticker = give_partner(COMPANIES, element.lower(), False)
    if not(is_company) and not(is_ticker):
      print(f'{element} is an unknown company or an unknown ticker symbol')
      continue
    if is_company:
      # здесь лежат [цена, ticker] или false
      price_action = give_partner(STOCKS, is_company[0].lower())
      # если какие-то ошибки в данных.
      print(f'{is_company[1]} stock price is {price_action[0]}') if price_action and len(price_action) > 1 else print(f'{is_company[1]} stock price is unknown')
      continue    
    if is_ticker:
      print(f'{is_ticker[1]} is a ticker symbol for {is_ticker[0]}')
      continue 

  return

#проверяет, есть ключ в dict игнорируя регистр 2-ый способ, можно доделать потом
# def detect_element_is_keys(element, dict_elements):
#   element_low = element.lower()


# def get_dict_with_lower_keys(dict):
#   return {k.lower(): v for k,v in dict.items()}

# def get_dict_with_lower_value(dict):
#   return {k: v.lower() for k,v in dict.items()}

def give_key_by_value(dict, value):
  for k,v in dict.items():
    if v == value: return k 
  return False

# второй способ
def give_partner(dict, key, pattern_by_key = True):
  key_lower = key.lower()
  if pattern_by_key:
    for k,v in dict.items():
      if k.lower() == key_lower: return [v, k]
    return False
  else: 
    for k,v in dict.items():
      if v.lower() == key_lower: return [k, v]
    return False

def break_down_into_elements(str_elements, count_elements = False):
  if len(str_elements) == 0: return False

  list_elements = ['']
  sep_elements = ','
  skip_element = ' ' # если бы было несколько, то массив

  for ch in str_elements:
    index_now_element = len(list_elements) - 1
    if ch == skip_element: continue
    if ch == sep_elements:
      if len(list_elements[index_now_element]) == 0: return False
      list_elements[index_now_element] = list_elements[index_now_element]
      list_elements.append('')
      continue
    list_elements[index_now_element] = list_elements[index_now_element] + ch
  
  len_list_elements = len(list_elements)

  if len(list_elements[len_list_elements - 1]) == 0: return False
  if count_elements or count_elements == 0:
    return list_elements if len_list_elements == count_elements else False
  
  return list_elements
if __name__ == '__main__':
  if len(sys.argv) != 2 : 
    # print('Нужно ввести строку из 3 слов через ","')
    sys.exit(0)

  elements = break_down_into_elements(sys.argv[1], 3)
  if not(elements): sys.exit(0)
  detect_ticker_or_company(elements)