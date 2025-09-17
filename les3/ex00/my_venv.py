import os

def create_venv():
    if os.path.exists('venv'):
        return True

    os_name = os.name
    if os_name == 'nt':
        os.system('python -m venv venv')
        print(f'os name: {os_name}')
        if os.path.exists('venv'): 
            return True
    
    if os_name == 'posix':
        os.system('python3 -m venv venv')
        if os.path.exists('venv'): 
            return True
        
    return False

# доработать 
def activate_venv():

    os_name = os.name
    if os_name == 'nt':
        result_code = os.system('venv\\Scripts\\activate')

        if result_code == 0:
            print(f'os name: {os_name} venv activate') 
            return True
    
    if os_name == 'posix':
        result_code = os.system('source venv/bin/activate')
        if result_code == 0: 
            print(f'os name: {os_name} venv activate')
            return True
        
    return False

def deactivate_venv():
    if os.system('deactivate') == 0:
        print('deactivate venv: success')
    else: 
        print('deactivate venv: error')   

def install_requirements():
    # можно задать глобально или через консоль
    path_req = './requirements.txt'

    if not os.path.exists(path_req):
        print(f"Not file: {path_req}")
        return
    
    os.system(f'pip install -r {path_req}')
    print('Requirements install')
    return

def print_name_env():
    virtual_env_path = os.environ.get('VIRTUAL_ENV')

    if virtual_env_path:
        print(f"Your current virtual env is {virtual_env_path}")
        return True
    else:
        print("Your current virtual env is not found")
        return False


if __name__ == '__main__':
    # пока не доработаю, не трогать
    # if not create_venv(): print('Error create local venv!')

    # activate_venv()
    # print_name_env()
    if print_name_env(): install_requirements()


    