import sys


class Research:
    def __init__(this, path):
        this.file_path = path

    def file_reader(self, file_path=' '):
        path = self.file_path
        try:
            with open(path, 'r') as file_r:
                is_header = True
                content = []

                for line in file_r:
                    line_content = self.get_content_line(line)
                    if not line_content:
                        print("No correct structure (2)")
                        sys.exit(2)

                    if len(line_content) != 2:
                        print("No correct structure (2)")
                        sys.exit(2)

                    if is_header:

                        line_content = self.transform_list_to_string(
                            line_content)
                        content.append(line_content)
                        is_header = False
                        # print(line_content)
                        continue

                    for element in line_content:
                        if element not in ['1', '0']:
                            print("No correct structure (3)")
                            sys.exit(3)

                    line_content = self.transform_list_to_string(line_content)
                    content.append(line_content)
                # print(content)
                return self.create_response(True, content)
        except FileNotFoundError:
            # print('File not found!')
            return self.create_response(False, 'File not found!')
        except Exception as e:
            # print(f'Error: {e}')
            return self.create_response(False, f'Error: {e}')

    def create_response(self, success, body):
        return {'success': success, 'content': body} if success else {'success': success, 'error': body}

    # sep - разделитель элементов (по умолчанию запятая)
    def get_content_line(self, line, sep=','):
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

    # sep - разделитель элементов (по умолчанию запятая)
    def transform_list_to_string(self, list_content, sep=','):
        line_end = '\n'
        result_transform = ''
        len_content = len(list_content)
        for i in range(len_content):
            result_transform += list_content[i] + sep if i < len_content - 1 \
                else list_content[i]

        return result_transform + line_end

    def print_list(self, list_items, end_str='\n'):
        for item in list_items:
            print(item, end=end_str)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Arguments passed incorrectly.\nFile path required')
        sys.exit(1)
    research = Research(sys.argv[1])
    result_read = research.file_reader()

    if result_read['success']:
        research.print_list(result_read['content'], end_str='')
        sys.exit(0)
    else:
        print(result_read['error'])
