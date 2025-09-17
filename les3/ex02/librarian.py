import os
import sys


class Librarian:
    def __init__(self, name_venv):
        self.name_venv = name_venv
        self.os_win = 'nt'
        self.os_unit = 'posix'

    def check_correct_virtual_env(self):
        virtual_env_path = os.environ.get("VIRTUAL_ENV")
        if not virtual_env_path:
            print('Not start virtual env')
            sys.exit(0)

        os_name = os.name
        if os_name == self.os_unit:
            current_directory = os.getcwd()
            last_element_directory = current_directory[current_directory.rfind(
                '/'):]
            virtual_path = f'{last_element_directory}/{self.name_venv}'
            if virtual_path in virtual_env_path:
                print('correct virtual env')
                return True
            return False
        if os_name == self.os_win:
            current_directory = os.getcwd()
            last_element_directory = current_directory[current_directory.rfind(
                '\\'):]
            virtual_path = f'{last_element_directory}\\{self.name_venv}'
            if virtual_path in virtual_env_path:
                print('correct virtual env')
                return True
            return False

    def install_libraries(self, file_path):
        try:
            with open(file_path, 'r') as file_libs:
                libs = file_libs.read()
                command_install = f'pip install {libs}'
                print(f'installing: {libs}')
                try:
                    # или f'pip install -r {file_path}'
                    is_install = os.system(command_install)
                    return True
                except Exception as e:
                    print(f'Error: {e}')
                    return False

        except FileNotFoundError:
            print('file dependency not found')
        except Exception as e:
            print(f'Error: {e}')

    def save_txt_requirements(self):
        try:
            os.system('pip freeze > requirements.txt')
            return True
        except Exception as e:
            print(f'Error: {e}')
            return False


if __name__ == '__main__':
    librarian = Librarian('wanitaro')
    is_check_virtual = librarian.check_correct_virtual_env()
    if not is_check_virtual:
        print('not correct virtual env')
        sys.exit(1)

    is_install_libraries = librarian.install_libraries('./dependency.txt')
    if not is_install_libraries:
        print('Not correct install libraries')
        sys.exit(2)

    is_save_txt_requirements = librarian.save_txt_requirements()
    if not is_save_txt_requirements:
        print('Not correct save text file with this requirements')
        sys.exit(3)

    print('program success')
