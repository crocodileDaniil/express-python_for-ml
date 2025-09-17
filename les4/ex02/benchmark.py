#!/usr/bin/python3

import timeit
import sys

examples_email = ['john@gmail.com', 'james@gmail.com', 'alice@yahoo.com', 
'anna@live.com', 'philipp@gmail.com']

emails =[ *['john@gmail.com', 'james@gmail.com', 'alice@yahoo.com', 
'anna@live.com', 'philipp@gmail.com'] * 5 ]

def standart_method(list_enum, pattern):
    result = []
    for item in list_enum:
        if pattern in item:
            result.append(item)
    return result

def use_list_compr(list_enum, pattern):
    result = [ item for item in list_enum if pattern in item ]

    return result
#если возвращать каждый раз list, то получается много времени. Если применить list после, то времени становится меньше
def use_map(list_enum, pattern):     
    return map(lambda email:email if pattern in email else None, list_enum)

def print_results(rs_list):
    l_len = len(rs_list)

    for i in range(l_len):
        if i < l_len - 1:
            print(rs_list[i], end=' vs ')
        else:
            print(rs_list[i])

def use_filter(list_enum, pattern):  
    # def func_filter(email):
    #     return

    return filter(lambda email: True if pattern in email else False, list_enum)

def execute_porgam(type_func='loop', repeat=10000):
    repeat_standart = 90_000_000
    repeat_test = 3000
    time_results = []
    pattern = '@gmail'

    dict_functions = {
        'loop': standart_method,
        'list_comprehension': use_list_compr,
        'map': use_map,
        'filter': use_filter
    }

    time_r = timeit.timeit(lambda: dict_functions[type_func](emails, pattern), number=repeat)

    # time_map = timeit.timeit(lambda: use_map(emails, pattern), number=repeat_test)
    # time_filter = timeit.timeit(lambda: use_filter(emails, pattern), number=repeat_test)

    # print(use_map(emails, pattern))
    # print(use_filter(emails, pattern))
    # print(time_map)
    # print(time_filter)

    result = list(dict_functions[type_func](emails, pattern)) if type_func in ['map', 'filter'] else dict_functions[type_func](emails, pattern)
    
    print(result)
    print(time_r)

    pass

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Input type func: loop, list_comprehension, map, filter and count repeat ")
        sys.exit(1)

    execute_porgam(sys.argv[1], int(sys.argv[2]))