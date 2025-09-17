#!/usr/bin/python3

import timeit
import sys
from functools import reduce


def use_loop(numbers):
    result = 0
    # for i in range(1, number_border + 1)
    for num in numbers:
        result += num**2

    return result


def use_reduce(numbers):

    return reduce(lambda x, y: x + y ** 2, numbers)
    # return reduce(lambda x, y: x + y **2, [*range(1, number_border+1)])


def execute_program(type_func='loop', repeat=10000, border_summ=5):
    repeat_standart = 90_000_000
    repeat_test = 3000

    dict_functions = {
        'loop': use_loop,
        'reduce': use_reduce
    }
    numbers = range(1, border_summ+1)
    # можно передать ещё число, разница в скорости несущественная
    time_r = timeit.timeit(
        lambda: dict_functions[type_func](numbers), number=repeat)

    result = use_loop(numbers)

    # print(result)
    print(f'{time_r:0.9f}')
    pass


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print("Input type func: loop, reduce, and count repeat, and border_number ")
        sys.exit(1)
    try:
        execute_program(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    except Exception as e:
        print('No correct args')
        print("Input type func: loop, reduce, and count repeat - int, and border_number - int ")
        print(f'Error: {e}')
