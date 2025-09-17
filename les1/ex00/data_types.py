def data_types():
    var_1 = 1
    var_2 = "hello world"
    var_3 = 2.0
    var_4 = True
    var_5 = [4, 'python', 4.45]
    var_6 = {
        'name': 'Daniil',
        'age': 25,
        'city': 'Lipetsk',
    }
    var_7 = (1, 2, 3)
    var_8 = {7, "name", 2.3}

    types_list = [get_type(var_1), get_type(var_2), get_type(var_3),
                  get_type(var_4), get_type(var_5), get_type(var_6),
                  get_type(var_7), get_type(var_8)]

    print(create_str_result(types_list))

def get_type(var):
    return type(var).__name__

def create_str_result(arr_type):
    result = "["
    len_list = len(arr_type)

    for i in range(0, len_list):
        result += (arr_type[i] + ", " if i < len_list - 1 else arr_type[i] + ']')

    return result
    # for type in arr_type:
    #     result += type + ", "
    # return result[:-2] + "]"

if __name__ == '__main__':
    data_types()