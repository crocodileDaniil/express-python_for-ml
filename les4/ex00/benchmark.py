#!/usr/bin/python3

import timeit

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

def print_results(rs_list):
    l_len = len(rs_list)

    for i in range(l_len):
        if i < l_len - 1:
            print(rs_list[i], end=' vs ')
        else:
            print(rs_list[i])

def execute_porgam():
    repeat = 90_000_000
    repeat_test = 3000
    time_results = []
    pattern = '@gmail'

    rs_standart = standart_method(emails, pattern)
    rs_list_compr = use_list_compr(emails, pattern)
    # print(f"result standart: {rs_standart}")
    # print(f"result ist compr: {rs_list_compr}")


    time_rs_standart = timeit.timeit(lambda: standart_method(emails, pattern), number=repeat_test)
    time_rs_list_compr = timeit.timeit(lambda: use_list_compr(emails, pattern), number=repeat_test)

    time_results.extend([time_rs_standart, time_rs_list_compr])


    sort_time_results = sorted(time_results)

    if time_rs_standart > time_rs_list_compr:
        print('it is better to use a list comprehension')
    else:
        print('it is better to use a loop')

    print_results(sort_time_results)

    pass

if __name__ == '__main__':
    # print('start')
    execute_porgam()