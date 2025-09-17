from research import Research
from random import randint
from config import logger

class Analytics(Research.Calculations):
    def __init__(self, data_parent):
        super().__init__(data_parent)

    def predict_random(self, count_prediction):
        result_pred = []
        for i in range(count_prediction):
            result_pred.append([0, 0])

        for pred in result_pred:
            if randint(0, 1) == 1:
                pred[0] += 1
            else:
                pred[1] += 1
        logger.info('random - success')
        return result_pred

    def predict_last(self, list_elements):
        len_list = len(list_elements)
        if len_list == 0:
            return False
        logger.info('last - success')
        return list_elements[len_list - 1]

    def save_file(self, data, name, type='txt'):
        file_write = f'{name}.{type}'
        try:
            with open(file_write, 'w') as file_w:
                file_w.write(data)
            logger.info('save - success')
            Research.message_telegram('Report success')
        except Exception as e:
            logger.info(f'save - error: {e}')
            Research.message_telegram(f'Report failed.\n Error: {e}')
        return
