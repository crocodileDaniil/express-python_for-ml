import pstats


p = pstats.Stats('output.prof')

# количество вызовов и сохранение в файл.
p.sort_stats('ncalls').print_stats()  
p.sort_stats('ncalls').dump_stats('profiling-ncalls.txt') 

# накопленное время и 5 функий и файл
p.sort_stats('cumulative').print_stats(5)
p.sort_stats('cumulative').dump_stats('pstats-cumulative.txt') 

# т.к. он сохраняет в бинарные файлы, то необходимо перезаписать
with open("profiling-ncalls.txt", "w") as f:
    stats = pstats.Stats("output.prof", stream=f)
    stats.sort_stats("ncalls")
    stats.print_stats()

with open("pstats-cumulative.txt", "w") as f:
    stats = pstats.Stats("output.prof", stream=f)
    stats.sort_stats("cumulative")
    stats.print_stats(5)