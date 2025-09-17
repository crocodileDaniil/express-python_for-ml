def to_dictionary():
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
    
    transform_dict = transform_to_dict(list_of_tuples)
    sort_dict = dict(sorted(transform_dict.items(),  key=lambda item: int(item[0]), reverse = True))

    m_len_key = max_len_key(sort_dict)
    
    print_result(sort_dict, m_len_key)

    return

def transform_to_dict(original_list):
    transform_dict = {}

    for element in original_list:
        country = element[0]
        country_number = element[1]
        if country_number in transform_dict:
            transform_dict[country_number].append(country)
        else:
             transform_dict[country_number] = [country]


    return transform_dict

def print_result(dict_v, sep_len):
    for k,v in dict_v.items():
        len_countrys = len(v)
        if len_countrys != 1:
            for county in v:
                print(f"{(sep_len - len(k)) * ' '}'{k}' : '{county}'")
        else:
            print(f"{(sep_len - len(k)) * ' '}'{ k}' : '{v[0]}'")

def max_len_key(dict_v):
    max_len = 0
    for k,v in dict_v.items():
        len_k = len(k)
        if len_k > max_len: max_len = len_k 
    return max_len

if __name__ == '__main__':
    to_dictionary()