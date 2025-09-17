from research import Research
from random import randint
import sys


class Analytics(Research.Calculations):
    def __init__(self, data_parent):
        super().__init__(data_parent)

    def predict_random(self, count_prediction):
        result_pred = []
        for i in range(count_prediction):
            result_pred.append([0, 0])

        for pred in result_pred:
            if randint(0, 1) == 1:
                pred[0] += 1
            else:
                pred[1] += 1

        return result_pred

    def predict_last(self, list_elements):
        len_list = len(list_elements)
        if len_list == 0:
            return False

        return list_elements[len_list - 1]
    
    def save_file(self, data, name, type='txt'):
        file_write = f'{name}.{type}'
        try:
            with open(file_write, 'w') as file_w:
                file_w.write(data)
        except Exception as e:
            print(f'Error read is: {e}')

def print_elements_list(list_elements):
    for element in list_elements:
        print(element, sep=" ", end=" ")
    print()


def execute_program():
    len_argv = len(sys.argv)

    if len_argv != 2 and len_argv != 3:
        print("Arguments passed incorrectly.\nFile path required ..[has_header]")
        sys.exit(1)

    path = sys.argv[1]
    has_header = None
    if len_argv == 2:
        research = Research(path)
        result_read = research.file_reader()
        if result_read["success"]:
            content = result_read["content"]
            print(content)

            calculator_statistics = Analytics(content)
            count_throws = calculator_statistics.counts()
            statistics_throws = calculator_statistics.fractions()
            predictions = calculator_statistics.predict_random(3)
            last_element = calculator_statistics.predict_last(predictions)

            print_elements_list(count_throws)
            print_elements_list(statistics_throws)
            print(*predictions)
            print(last_element)

            sys.exit(0)
        else:
            print(result_read["error"])

    elif len_argv == 3:
        has_header = sys.argv[2]
        if has_header:
            research = Research(path)
            result_read = research.file_reader(has_header)
            if result_read["success"]:
                content = result_read["content"]
                print(content)

                calculator_statistics = Analytics(content)
                count_throws = calculator_statistics.counts()
                statistics_throws = calculator_statistics.fractions()
                predictions = calculator_statistics.predict_random(3)
                last_element = calculator_statistics.predict_last(predictions)

                print_elements_list(count_throws)
                print_elements_list(statistics_throws)
                print(*predictions)
                print(last_element)

                sys.exit(0)
        else:
            print('Non correct pattern "has_header"')
            sys.exit(1)


# if __name__ == "__main__":
#     execute_program()
