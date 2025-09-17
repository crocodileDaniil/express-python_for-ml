class Research:
    path = './data.csv'    
    
    def file_reader(self, file_path='./data.csv'):
        try:
            with open(path, 'r') as file_r:
                content = file_r.read()
                result = {"success": True,"content": content}
                return result
        except FileNotFoundError:
            # print('File not found!')
            return {'success': False,'error': 'File not found!'}
        except Exception as e:
            # print(f'Error: {e}')
            return {'success': False, 'error': f'Error: {e}'}

if __name__ == '__main__':
    path = './data.csv'
    research = Research()
    result_read = research.file_reader(path)

    if result_read['success']:
        print(result_read['content'])
    else:
        print(result_read['error'])
