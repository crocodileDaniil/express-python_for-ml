import sys

#Исключения, вызванные функцией open(), не подлежат обработке.
def name_extractor(e_mail):
    read_path ='./employees.tsv'
    name = ''
    with open(read_path, 'r') as file_r:
      for line in file_r:
          if e_mail in line:
            name = get_name(line[0:-1])
            break

    if len(name) == 0: 
       print('Not found name')
       return

    correct_paragraph = get_paragraph(name)
    print(correct_paragraph)
    return correct_paragraph

def get_paragraph(name):
   return (f'Dear {name}, welcome to our team.' 
           f'We are sure that it will be a pleasure to work with you.' 
           f'That’s a precondition for the professionals that our company hires.')

def get_name(line):
    border_name = '\t'
    name = ''

    for ch in line:
      if ch == border_name:
         break
      name += ch

    return name

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Нужно ввести e-mail пользвателя')
        sys.exit(0)

    name_extractor(sys.argv[1])
