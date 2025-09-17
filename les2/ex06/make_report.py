from research import Research
from analytics import Analytics
from config import *
import requests


def execute_program():
    global file_path
    global has_header
    global count_prediction
    global name_file_write
    global type_file_write

    logger.info('program start')
    research = Research(file_path)
    result_read = research.file_reader(has_header)
    if result_read["success"]:
        content = result_read["content"]

        calculator_statistics = Analytics(content)
        count_throws = calculator_statistics.counts()
        statistics_throws = calculator_statistics.fractions()
        predictions = calculator_statistics.predict_random(count_prediction)
        last_element = calculator_statistics.predict_last(predictions)
        count_predictions = calculator_statistics.counts(predictions)

        text_report = create_report(count_throws[0] + count_throws[1], count_throws[1], count_throws[0], 
                      statistics_throws[1], statistics_throws[0], count_prediction, count_predictions[1], count_predictions[0])

        calculator_statistics.save_file(text_report,name_file_write, type_file_write)
        logger.info('program end - success')

def print_elements_list(list_elements):
    for element in list_elements:
        print(element, sep=" ", end=" ")
    print()

def create_report(all_try, c_tails, c_heads, s_tail, s_head, count_th, th_count_tails, th_count_heads):
    logger.info('report - start')
    # можно global нужен есил происходит замена, поэтому можно закоментировать
    # global replace_all_try 
    # global replace_tails
    # global replace_heads
    # global replace_stat_tail
    # global replace_stat_head
    # global replace_count_throws
    # global replace_th_count_tails
    # global replace_th_count_heads
    # global model_report

    report = model_report
    report = report.replace(replace_all_try, str(all_try))
    report = report.replace(replace_tails, str(c_tails))
    report = report.replace(replace_heads, str(c_heads))
    report = report.replace(replace_stat_tail, str(s_tail))
    report = report.replace(replace_stat_head, str(s_head))
    report = report.replace(replace_count_throws, str(count_th))
    report = report.replace(replace_th_count_tails, str(th_count_tails))
    report = report.replace(replace_th_count_heads, str(th_count_heads))

    logger.info('report - success')
    return report


if __name__ == "__main__":
    execute_program()
    