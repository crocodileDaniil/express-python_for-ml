import logging

file_path = './data.csv'
has_header = True
count_prediction = 3
name_file_write = 'report'
type_file_write = 'txt'

replace_all_try = '_all-try_'
replace_tails = '_tails_'
replace_heads = '_heads_'
replace_stat_tail = '_stat-tail_'
replace_stat_head = '_stat-head_'
replace_count_throws = '_count-throws_'
replace_th_count_tails = '_th-count-tails_'
replace_th_count_heads = '_th-count-heads_'

model_report = (f'We have made _all-try_ observations from tossing a coin: _tails_ of them were tails and _heads_ of them were heads.'
                f'The probabilities are _stat-tail_% and _stat-head_%, respectively.'
                f'Our forecast is that in the next _count-throws_ observations we will have: _th-count-tails_ tail and _th-count-heads_ heads.')

logger_format = "%(asctime)s %(funcName)s %(lineno)d %(message)s"
logger_name = "analytics.log"

logging.basicConfig(
    level=logging.INFO,
    filename=logger_name,
    filemode="w",
    format=logger_format
)

telegram_bot_token = '7651200420:AAEZeg3ZM8IKijieK2eka_c3w85AxUiqOE8'
# для проверка диалогов
#                                       TOKEN
# https://api.telegram.org/bot7651200420:AAEZeg3ZM8IKijieK2eka_c3w85AxUiqOE8/getUpdates
telegram_chat_id = '346455076'
telegram_url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    print(model_report)
