def transform_file(path_r='clean', path_s='clean'):
    content_write = []
    with open(path_r, 'r') as file_read:
        for line in file_read:
            line_list = create_list_from_line(line)
            line_str = convert_to_string_with_delimiter(line_list, '\t')
            content_write.append(line_str)
    with open(path_s, 'w') as file_write:
        for line in content_write:
            file_write.write(line)

def create_list_from_line(line):
    separator_column = ","
    border_column = '"'
    flag = False
    result = ['']
    for char in line:
        if char == border_column:
            flag = not(flag)
            continue
        if char == separator_column and not(flag):
            result.append('')
            continue
        result[len(result) - 1] += char
    return result

def convert_to_string_with_delimiter(lst, delimiter):
    bool_column = (4,5)
    len_lst = len(lst)
    result = ""
    line_separator = '\n'

    for i in range(len_lst):
        if line_separator in lst[i]:
            append_string = '"' + lst[i][:-2] + '"' if not(i + 1 in bool_column) else  lst[i][:-2]
        else:
            append_string = '"' + lst[i] + '"' if not (i + 1 in bool_column) else lst[i]
        result += (append_string + delimiter) if i < len_lst - 1 else append_string

    return result + line_separator

if __name__ == '__main__':
    transform_file('./ds.csv', './ds.tsv')