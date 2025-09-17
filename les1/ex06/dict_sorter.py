def to_sort():
    list_of_tuples = [
        ('Russia', '25'),
        ('France', '132'),
        ('Germany', '132'),
        ('Spain', '178'),
        ('Italy', '162'),
        ('Portugal', '17'),
        ('Finland', '3'),
        ('Hungary', '2'),
        ('The Netherlands', '28'),
        ('The USA', '610'),
        ('The United Kingdom', '95'),
        ('China', '83'),
        ('Iran', '76'),
        ('Turkey', '65'),
        ('Belgium', '34'),
        ('Canada', '28'),
        ('Switzerland', '26'),
        ('Brazil', '25'),
        ('Austria', '14'),
        ('Israel', '12')
        ]
    
    sorted_list = sort_list(list_of_tuples)
    transform_dict = transform_to_dict(sorted_list)
    # sort_dict = dict(sorted(transform_dict.items(),  key=lambda item: int(item[0]), reverse = True))

    
    print_result(transform_dict)    

    return

def sort_list(original_list):
  len_or_list = len(original_list)
  if len_or_list < 2: return False

  sorted_list = original_list
  
  while True:
      flag = False
      for i in range(len_or_list - 2):
          code_next = int(sorted_list[i + 1][1])
          code_now = int(sorted_list[i][1])
          if  code_next > code_now:
              flag = True
              sorted_list[i], sorted_list[i + 1] = sorted_list[i + 1], sorted_list[i]
          
          name_next = sorted_list[i + 1][0]
          name_now = sorted_list[i][0]
          if code_next == code_now:
              # в алфавитном порядке, это name_next > name_now
              # т.к. сначала должна идти germany потом france
              # но по заданию нужно изменить знак
              if name_next < name_now:
                  sorted_list[i], sorted_list[i + 1] = sorted_list[i + 1], sorted_list[i]
                  flag = True
                   
      if not(flag): break
  return sorted_list

def transform_to_dict(original_list):
    transform_dict = {}

    for element in original_list:
        country = element[0]
        country_number = element[1]
        if country in transform_dict:
            transform_dict[country].append(country_number)
        else:
             transform_dict[country] = [country_number]


    return transform_dict

def print_result(dict_v):
    
    for k,v in dict_v.items():
        print(k)
    return

if __name__ == '__main__':
    to_sort()