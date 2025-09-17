#!/usr/bin/python3

import sys
import resource

def get_content_file(path='./ratings.csv'):
  content_file = []
  with open(path, 'r') as file_r:
    for stroke in file_r:
      content_file.append(stroke)

  return content_file

def execute_program():
  full_time_start = get_full_time()
  content_ratings = get_content_file(sys.argv[1])

  for rating in content_ratings:
    pass

  full_time_end = get_full_time()
  memory_pick = round(get_peak_memory() / 2 ** 20, 3)
  print(f'Peak Memory Usage = {memory_pick} GB')  
  print(f'User Mode Time + System Mode Time = {round(full_time_end - full_time_start, 2)}s')
  print(f'completed {sys.argv[0]}')

def get_peak_memory():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_maxrss # возвращает в КБ

def get_full_time():
  user_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime
  system_time = resource.getrusage(resource.RUSAGE_SELF).ru_stime
  
  return user_time + system_time

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print('input file path')
    sys.exit(1)
  execute_program()