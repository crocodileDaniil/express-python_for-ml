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


def execute_porgam():
    repeat = 90_000_000
    repeat_test = 3000
    time_results = []
    pattern = '@gmail'

    rs_standart = standart_method(emails, pattern)
    rs_list_compr = use_list_compr(emails, pattern)
    re_list_map = list(use_map(emails, pattern))
    # print(f"result standart: {rs_standart}")
    # print(f"result ist compr: {rs_list_compr}")
    # print(f"result is map: {re_list_map}")


    time_rs_standart = timeit.timeit(lambda: standart_method(emails, pattern), number=repeat_test)
    time_rs_list_compr = timeit.timeit(lambda: use_list_compr(emails, pattern), number=repeat_test)
    time_rs_list_map = timeit.timeit(lambda: use_map(emails, pattern), number=repeat_test)

    times_dict = {
        time_rs_standart: "loop",
        time_rs_list_compr: "list comprehension",
        time_rs_list_map: "map"
    }
    min_time = min(time_rs_standart, time_rs_list_compr, time_rs_list_map)

    print(f"it is better to use a {times_dict[min_time]}")

    time_results.extend([time_rs_standart, time_rs_list_compr, time_rs_list_map])

    # print(f"times standart: {time_rs_standart}")
    # print(f"times ist compr: {time_rs_list_compr}")
    # print(f"times is map: {time_rs_list_map}")

    sort_time_results = sorted(time_results)

    print_results(sort_time_results)

    pass

if __name__ == '__main__':
    # print('start')
    execute_porgam()