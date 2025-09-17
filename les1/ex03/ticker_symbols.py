import sys
def print_company_and_price_action(ticker):
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

  ticker_lower = ticker.lower()
  companies_keys_lower = get_dict_with_lower_value(COMPANIES)
  stocks_keys_lower = get_dict_with_lower_keys(STOCKS)

  company = give_key_by_value(companies_keys_lower, ticker_lower)
  if not(company):
    print('Unknown ticker')
    return
  
  if ticker_lower not in stocks_keys_lower:
    print("not price action for company")
    return
  
  price_action = stocks_keys_lower[ticker_lower]

  print(f'{company} {price_action}')
  # print(f'{give_partner(COMPANIES, ticker, False)} {give_partner(STOCKS, ticker)}')
  
  return

def get_dict_with_lower_keys(dict):
  return {k.lower(): v for k,v in dict.items()}

def get_dict_with_lower_value(dict):
  return {k: v.lower() for k,v in dict.items()}

def give_key_by_value(dict, value):
  for k,v in dict.items():
    if v == value: return k 
  return False

# второй способ
def give_partner(dict, key, pattern = 'key'):
  key_lower = key.lower()
  if pattern == 'key':
    for k,v in dict.items():
      if k.lower() == key_lower: return v
    return False
  else: 
    for k,v in dict.items():
      if v.lower() == key_lower: return k
    return False

if __name__ == '__main__':
  if len(sys.argv) != 2 : 
    # print('Введите ключ для поиска')
    sys.exit(0)
  print_company_and_price_action(sys.argv[1])