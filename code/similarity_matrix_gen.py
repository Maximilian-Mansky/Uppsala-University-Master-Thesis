import numpy as np
import matplotlib.pyplot as plt
# import matplotlib
from gensim.models import KeyedVectors


model = KeyedVectors.load_word2vec_format('word2vec vectors.txt')
# with open('word2vec vocabulary.txt', 'r', encoding='utf8') as filecontents:
#     plain = filecontents.read()
# lines = plain.split('\n')



words = [str(x) for x in range(0, 20)] + [str(x) for x in range(21, 91, 5)] + ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
                                               'seventeen', 'twenty', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']
number_of_words = len(words)
indices = np.arange(len(words), dtype=np.int32)
carry_matrix = np.zeros((number_of_words, number_of_words), dtype=np.float32)
for counter1, index1 in enumerate(indices):
    for counter2, index2 in enumerate(indices):
        carry_matrix[counter1, counter2] = model.similarity(words[index1], words[index2])
carry_matrix = np.ma.array(carry_matrix - np.eye(number_of_words), mask=np.tril(np.ones((number_of_words,number_of_words)), k=-1))
## plot ##
font = {# 'fontname': 'Hoefler Text',
        'size': 6}
plt.rc('font', **font)
fig, axes = plt.subplots(figsize=(7, 7))
axes.spines['left'].set_visible(False)
axes.spines['bottom'].set_visible(False)
heatmap = plt.imshow(carry_matrix, vmin=-0.5, vmax=1.0, cmap=plt.cm.coolwarm)
plt.xticks(range(number_of_words), [words[index] for index in indices], rotation=-70, ha='right')
axes.xaxis.tick_top()
plt.yticks(range(number_of_words), [words[index] for index in indices])
axes.yaxis.tick_right()
# cbaxes = fig.add_axes([0, 0, 1, 0.1])
fig.colorbar(heatmap, orientation='horizontal', pad=0.0, shrink=0.845)
plt.savefig('simmat_numbers_ext.pdf', dpi=600, transparent=True, bbox_inches='tight')
# plt.show()