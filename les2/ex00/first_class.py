class Must_read:
    path = './data.csv'
    try:
        with open(path, 'r') as file_r:
            content = file_r.read()
            print(content)
    except FileNotFoundError:
        print('File not found!')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    first_class = Must_read()