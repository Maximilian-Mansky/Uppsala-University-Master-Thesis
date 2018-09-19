import numpy as np
from gensim.models import KeyedVectors, word2vec
import collections
import re


# with open('player number list.txt', 'r', encoding='utf8') as filecontents:
#     plain = filecontents.read()
# lines = plain.split('\n')
# names = {}
# for line in lines:
#     if not re.match('[a-zA-z\s]\n', line):
#         try:
#             number = line.split(' ')[0]
#             name = line.split(' ')[1].lower()
#             name = name.split(',')[0]
#             names[name] = number
#         except IndexError:
#             print(line)
# print(len(lines))

model = KeyedVectors.load_word2vec_format('word2vec vectors.txt')


# number_name_split = []
# correct_count = collections.Counter()
# counter = 0
# for name in names:
#     try:
#         value_list = []
#         most_common = []
#         number_name_split.append(model.similarity(name, str(names[name])))
#         for number in range(70):
#             value_list.append(model.similarity(name, str(number)))
#         for n in range(5):
#             most_common.append(value_list.index(max(value_list)))
#             del value_list[most_common[-1]]
#         if int(names[name]) in most_common:
#             correct_count[most_common.index(int(names[name]))] += 1
#     except KeyError:
#         print(name)
#         counter += 1
#         continue
# print(counter)
# print(correct_count)
# print(np.average(number_name_split), '±', np.sqrt(np.var(number_name_split)))

## number query
names = ['barca', '']
for name in names:
    value_list = []
    for number in range(90):
        value_list.append(model.similarity(name, str(number)))
    n1 = value_list.index(max(value_list))
    del value_list[n1]
    n2 = value_list.index(max(value_list))
    del value_list[n2]
    n3 = value_list.index(max(value_list))
    del value_list[n3]
    n4 = value_list.index(max(value_list))
    del value_list[n4]
    n5 = value_list.index(max(value_list))
    string = name
    string += ' & ' + str(names[name])
    string += ' '.join([' & $\\begin{matrix} \\text{' + str(value) + '} \\\\ ' + str(model.similarity(name, str(value)))[:5] + ' \\end{matrix}$' for value in [n1, n2, n3, n4, n5]])
    string += '\\\\'
    print(string)
