import sys

#heads - орел, tail - решка
class Research:
    def __init__(this, path):
        this.file_path = path
    
    def file_reader(self, has_header = True, file_path=' '):
        path = self.file_path
        len_content = 2    
        try:
            with open(path, 'r') as file_r:
                is_header = True
                content = []
                
                for line in file_r:
                    line_content = self.get_content_line(line)
                    if not line_content:
                        print("No correct structure (2)")
                        sys.exit(2)
                    
                    if len(line_content) != len_content: 
                            print("No correct structure (2)")
                            sys.exit(2)
                    
                    if is_header and  has_header:  
                        is_header = False
                        continue
                        # content.append(line_content)
                        # print(line_content)
                        continue
                    
                    for element in line_content:
                        if element not in ['1', '0']:
                            print("No correct structure (3)")
                            sys.exit(3)
                    
                    content.append(line_content)
                content = self.transform_to_num(content)
                return self.create_response(True, content)
        except FileNotFoundError:
            print('File not found!')
            return self.create_response(False,'File not found!')
        except Exception as e:
            print(f'Error: {e}')
            return self.create_response(False, f'Error: {e}')
        

    def create_response(self, success, body):
        return {'success': success, 'content': body} if success else \
            {'success': success, 'error': body}
    
    # sep - разделитель элементов (по умолчанию запятая)
    def get_content_line(self, line, sep = ','):
        result = ['']

        for ch in line:
            len_res = len(result)
            if ch == '\n':
                continue
            if ch == sep:
                result.append('')
                continue
            result[len_res - 1] = result[len_res - 1] + ch
        # print(f'get content line:\n{result}')
        return result
    
    # если заранее известна структура
    def transform_to_num(self, list_elements):
        list_to_num = []
        for elements in list_elements:
            nested_list = []
            for element in elements:
                nested_list.append(int(element))
            list_to_num.append(nested_list)
  
        return list_to_num
    
    class Calculations:
        def counts(self,list_throws):
            len_list_throws = len(list_throws)
            if len_list_throws == 0: return False
            count_headers_tails = [0, 0]

            for throw in list_throws:
                if throw[0] == 1: count_headers_tails[0] += 1
                else: count_headers_tails[1] += 1
            
            return count_headers_tails

        def fractions(self,distribution):
            if len(distribution) == 0: return False

            sum_distribution = sum(distribution)
            result = [dist/sum_distribution for dist in distribution ]

            return result


def is_bool(arg_start):
    return arg_start in ['true', 'false']

def transform_bool(arg_start):
    return True if arg_start == 'true' else False

def print_elements_list(list_elements):
    for element in list_elements:
        print(element, sep=' ', end=' ') 
    print()

def execute_program():
    len_argv = len(sys.argv)

    if len_argv != 2 and len_argv != 3:
        print('Arguments passed incorrectly.\nFile path required ..[has_header]') 
        sys.exit(1)

    path = sys.argv[1]
    has_header = None
    if len_argv == 2:
           research = Research(path)
           result_read = research.file_reader()
           if result_read['success']:
                content = result_read['content']     
                print(content)

                calculator_statistics_throws = research.Calculations()
                count_throws = calculator_statistics_throws.counts(content)
                statistics_throws = calculator_statistics_throws.fractions(count_throws)

                print_elements_list(count_throws)
                print_elements_list(statistics_throws)

                sys.exit(0)
           else:
                print(result_read['error'])

    elif len_argv == 3:
        has_header = is_bool(sys.argv[2].lower())
        if has_header:
            has_header = transform_bool(sys.argv[2].lower())
            research = Research(path)
            result_read = research.file_reader(has_header)
            if result_read['success']:
                content = result_read['content']     
                print(content)

                calculator_statistics_throws = research.Calculations()
                count_throws = calculator_statistics_throws.counts(content)
                statistics_throws = calculator_statistics_throws.fractions(count_throws)

                print_elements_list(count_throws)
                print_elements_list(statistics_throws)

                sys.exit(0)
        else:
            print('Non correct pattern "has_header"')
            sys.exit(1)

if __name__ == '__main__':
    execute_program()
