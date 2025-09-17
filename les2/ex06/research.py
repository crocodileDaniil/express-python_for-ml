import sys
import logging
import requests
import config 

#heads - орел, tail - решка
class Research:
    def __init__(this, path):
        this.file_path = path
        this.logger = logging.getLogger(__name__)
    
    def file_reader(self, has_header = True, file_path=' '):
        path = self.file_path
        len_content = 2 
        if not self.is_bool(str(has_header).lower()): 
            self.logger.error('Not correct pattern "has_header"')
            return self.create_response(False, 'Not correct pattern "has_header"')
        has_header = self.transform_bool(str(has_header).lower())
        self.logger.info('read start')
        try:
            with open(path, 'r') as file_r:
                is_header = True
                content = []
                
                for line in file_r:
                    line_content = self.get_content_line(line)
                    if not line_content:
                        self.logger.error("No correct structure (2)")
                        sys.exit(2)
                    
                    if len(line_content) != len_content: 
                            self.logger.error("No correct structure (2)")
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
                            self.logger.error('No correct structure (3)')
                            sys.exit(3)
                    
                    content.append(line_content)
                content = self.transform_to_num(content)
                self.logger.info("read file - success")
                return self.create_response(True, content)
        except FileNotFoundError:
            self.logger.error('File not found!')
            return self.create_response(False,'File not found!')
        except Exception as e:
            self.logger.error(f'Error: {e}')
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
    @staticmethod
    def message_telegram(message,chat_id='', url=''):

        if not chat_id: chat_id = config.telegram_chat_id
        if not url: url = config.telegram_url

        payload = {
            "chat_id": chat_id,
            "text": message
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            config.logger.info('Message Telegram completed')
        else: 
            config.logger.info(f'sending error message: {response.text} ')
    
    class Calculations:
        def __init__(self, data_statistics):
            self.data_statistics = data_statistics
            self.logger = logging.getLogger(__name__)
            
        def counts(self,list_throws=[]):
            self.logger.info('count start')
            len_list_throws = len(self.data_statistics)
            if len_list_throws == 0: return False
            count_headers_tails = [0, 0]

            if not list_throws:
                for throw in self.data_statistics:
                    if throw[0] == 1: count_headers_tails[0] += 1
                    else: count_headers_tails[1] += 1
            else:
                for throw in list_throws:
                    if throw[0] == 1: count_headers_tails[0] += 1
                    else: count_headers_tails[1] += 1
            self.logger.info('count - success')
            return count_headers_tails

        def fractions(self,distribution=[]):
            self.logger.info('result start')
            dist_calc = []
            if not distribution:
                dist_calc = self.counts(self.data_statistics)
            else:
                dist_calc = distribution
            if len(dist_calc) == 0: return False

            sum_distribution = sum(dist_calc)
            result = [round(dist/sum_distribution,2) for dist in dist_calc]

            self.logger.info('result - success')
            return result

    def is_bool(self, value):
        return value in ["true", "false"]
    
    def transform_bool(self, value):
        return True if value == "true" else False