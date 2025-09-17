#!/usr/bin/python3

import timeit
import random
from collections import Counter


class Benchmark:
    def __init__(self, numbers=None):
        if not numbers: 
            self.numbers = [random.randint(0, 100) for _ in range(1_000_000)]
        else:
            self.numbers = numbers
    def create_dict_numbers(self, numbers=None):
        if not numbers: numbers = self.numbers

        result = {}

        for number in numbers:
            if not number in result:
                result[number] = 1
            else:
                result[number] += 1

        return result

    def get_top_numbers(self, numbers, top):
        top_numbers = sorted(numbers.items(), key=lambda number: int(number[1]), reverse=True) #вернёт массив
        return [ number[0] for number in top_numbers[:top]]

    def my_sorted(self, numbers, top):
        values_numbers = [ int(item[1]) for item in numbers.items() ]
        length_sort = len(values_numbers)

        while True:
            flag_end = True
            
            for i in range(length_sort):
                if i == length_sort - 1:
                    continue
                if values_numbers[i + 1] > values_numbers[i]:
                    values_numbers[i + 1], values_numbers[i] = values_numbers[i], values_numbers[i + 1]
                    flag_end = False
            
            if flag_end: break

        sort_numbers = {}

        def key_for_value(value):
            for key, v in numbers.items():
                if value == v:
                    return key
                
        for num in values_numbers:
            key = key_for_value(num)
            sort_numbers[key] = num

        sort_numbers = list(sort_numbers)
        
        return sort_numbers[:10]
    
    def create_dict_numbers_use_counter(self, numbers=None):
        if not numbers: numbers = self.numbers

        result = Counter(numbers)

        return result

    def get_top_numbers_use_counter(self, numbers_counter, top):
        top_numbers = numbers_counter.most_common(top)

        return [element[0] for element in top_numbers]


def execute_program(numbers=None):

    benchmark = Benchmark()

    numbers_generate = benchmark.create_dict_numbers()
    top_result_sorted = benchmark.get_top_numbers(numbers_generate,10)
    top_result_my_sort = benchmark.my_sorted(numbers_generate,10)

    numbers_generate_use_counter = benchmark.create_dict_numbers_use_counter()
    numbers_top = benchmark.get_top_numbers_use_counter(numbers_generate_use_counter, 10)



    time_r_my_func = timeit.timeit(
        lambda: benchmark.create_dict_numbers(), number=1)
    time_t_r_my_func = timeit.timeit(
        lambda: benchmark.get_top_numbers(numbers_generate,10), number=1) #time_top_result
    time_t_r_custom_my_func = timeit.timeit(
        lambda: benchmark.my_sorted(numbers_generate,10), number=1)
    
    time_r_counter = timeit.timeit(
        lambda: benchmark.create_dict_numbers_use_counter(), number=1)
    time_t_r_counter = timeit.timeit(
        lambda: benchmark.get_top_numbers_use_counter(numbers_generate_use_counter,10), number=1)


    dict_times = {
        'my functions': time_r_my_func,
        'Counter': time_r_counter,
        'my top': time_t_r_my_func,
        'my top custom': time_t_r_custom_my_func,
        "Counter's top": time_t_r_counter
    }

    for k,v in dict_times.items():
        print(f'{k}: {v:0.9f}')

    # результаты моих функций
    # print(numbers_generate)
    print(top_result_sorted)
    print(top_result_my_sort)

    #результаты Counter
    # print(numbers_generate_use_counter)
    # print(numbers_top)

    # print(time_r_my_func, time_t_r_my_func, time_t_r_custom_my_func)
    # print(f'sorted: {(time_r_my_func + time_t_r_my_func):0.9f}')
    # print(f'full my: {(time_r_my_func + time_t_r_custom_my_func):0.9f}')
    # print(f'use counter: {(time_r_counter + time_t_r_counter):0.9f}')
    


if __name__ == '__main__':
    execute_program()
