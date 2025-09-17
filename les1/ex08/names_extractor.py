import sys

#Исключения, вызванные функцией open(), не подлежат обработке.
def name_extractor(path):
    write_path ='./employees.tsv'
    separator_elements = '\t'
    end_line = '\n'

    head_output_file = f'Name{separator_elements}Surname{separator_elements}E-mail{end_line}'
    content_write = [head_output_file]

    with open(path, 'r') as file_r:
      # contents = file_r.read()
      # print(contents)
      for line in file_r:
          # print(line)
          write_line = get_content_line(line[0:-1])
          content_write.append(write_line)
    
    # print(content_write)
    with open(write_path, 'w') as file_w:
       for write_line in content_write:
          file_w.write(write_line)

    return

def get_content_line(line):
    separator_result = '\t'
    separator_initials = '.'
    end_initials = '@'
    end_line = '\n'
    email_pattern = '@corp.com'
    result = ''
    is_upper = True

    for ch in line:
      if ch == separator_initials:
         result += separator_result
         is_upper = True
         continue
      if ch == end_initials:
         result = result + separator_result + line
         break
      result += ch.upper() if is_upper else ch
      is_upper = False
    # можно ввести доп проверку если была ошибка в данных
    # if email_pattern not in line: result = result + separator_result + 'check email in source data'

    return result + end_line

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Нужно указать путь до файла')
        sys.exit(0)

    name_extractor(sys.argv[1])

    # если нужна обработка открытия
    # try:
    #   with open(path, 'r') as file:
    #     contents = file.read()
    #     print(contents)
    # except FileNotFoundError:
    #   print("Ошибка: Файл не найден.")
    # except Exception as e:
    #   print(f"Произошла ошибка: {e}")