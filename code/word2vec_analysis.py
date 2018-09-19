# import nltk
# from nltk.corpus import gutenberg
from gensim.models import word2vec
# import logging
# from string import punctuation
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
# import sentiment
# import time
# import graphing
from sklearn.manifold import TSNE
import json
import re

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# tick = time.time()
# football_data = sentiment.load_raw_data('sportsmole commentary.json', 'commentary sportsmole')
# print('data loaded', time.time() - tick)
# football_data = ''.join(football_data).replace('.', '. ')
# print('joined and replaced', time.time() - tick)
# # football_data_sents = nltk.tokenize.sent_tokenize(football_data)
# # print('sentences tokenised', time.time() - tick)
# football_data_sans_punctuation = [[word.lower() for word in nltk.tokenize.word_tokenize(sent) if word not in punctuation] for sent in nltk.tokenize.sent_tokenize(football_data)]
# football_word2vec_model = word2vec.Word2Vec.load('sportsmole_test')


# print('punctuation removed', time.time() - tick)
# football_word2vec_model = word2vec.Word2Vec(football_data_sans_punctuation, min_count=25, size=200)
# print('model built', time.time() - tick)
# football_word2vec_model.save('sportsmole_test')
# football_word2vec_model.wv.save_word2vec_format('sportsmole_test_org', 'sportsmole_test_vocabulary')
#
#

def nearest_neighbours(starting_word, number_of_neighbours=10, dense=False, graphing=True):
    import graphing
    starting_word = starting_word.lower()
    starting_connections = football_word2vec_model.most_similar([starting_word.lower()], topn=number_of_neighbours)
    connection_dictionary = {starting_word: starting_connections}
    list_of_uniques = [starting_word] + [name for name, distance in starting_connections]
    for people in starting_connections[:]:
        people_list = football_word2vec_model.most_similar([people[0]], topn=number_of_neighbours)
        connection_dictionary[people[0]] = people_list
        list_of_uniques += [name for name, distance in people_list if not name in list_of_uniques]
    connection_matrix = np.zeros((len(list_of_uniques), len(list_of_uniques)), dtype=np.float32)
    connections = []
    for start in connection_dictionary:
        connections += [(start, end, distance) for (end, distance) in connection_dictionary[start][:]]
    if dense:
        for counter, name in enumerate(list_of_uniques):
            for second_counter, second_name in enumerate(list_of_uniques):
                connection_matrix[counter, second_counter] = football_word2vec_model.wv.similarity(name, second_name)
    else:
        for start, end, distance in connections:
            connection_matrix[list_of_uniques.index(start), list_of_uniques.index(end)] = distance
    position_matrix, graph_connections, quality = graphing.distance_builder(connection_matrix, list_of_uniques, 1000, 0.15, False)
    graphing.show_picture(list_of_uniques, position_matrix, graph_connections, quality)
    return 0


def a_is_to_b_as_x_is_to_(a, b, x):
    next_neighbours = football_word2vec_model.wv.most_similar(positive=[a, x], negative=[b])
    return next_neighbours


def t_SNE(word2vec_model, savefile_name, early_exaggeration=24, perplexity=30):
    X = word2vec_model[word2vec_model.wv.vocab]
    tsne = TSNE(n_components=2, early_exaggeration=early_exaggeration, perplexity=perplexity, init='pca')
    X_tsne = tsne.fit_transform(X)
    plt.rc('font', size=1)
    # figure_data = {}
    plt.scatter([-80, 80], [-80, 80], s=0.001)
    for counter, name in enumerate(word2vec_model.wv.vocab):
        # figure_data[name] = [float(X_tsne[counter, 0]), float(X_tsne[counter, 1])]
        # plt.scatter(X_tsne[counter, 0], X_tsne[counter, 1], s=5, color='tab:blue')
        plt.annotate(name, xy=(X_tsne[counter, 0], X_tsne[counter, 1]), xytext=(X_tsne[counter, 0], X_tsne[counter, 1]))
    # with open(datafile_name, 'w+', encoding='utf8') as filecontents:
    #     json.dump(figure_data, filecontents)
    plt.savefig(savefile_name, bbox_inches='tight', dpi=300, figsize=(11.7,16.6))
    # plt.show()
    plt.close()
    return 0

# test = t_SNE(football_word2vec_model, 't-SNE without words.pdf')

# for perplexity, early_exaggeration in [(55, 20), (55, 30), (55,40), (5, 50), (15, 50), (25, 50), (45, 50), (55, 50)]:
#     filename = 't-SNE ' + str(perplexity) + ' ' + str(early_exaggeration) + '.pdf'
#     do_thing = t_SNE(football_word2vec_model, filename, early_exaggeration, perplexity)
#     print(filename)
#
# test = t_SNE(football_word2vec_model)
teams = []
with open('team.json', 'r', encoding='utf8') as filecontents:
    data = json.load(filecontents)
for block in data:
    teams += [name for name in block['name'].lower().split() if not name in ['in', 'and', 'or']]

player_first = []
player_last = []
player_nick = []
with open('player.json', 'r', encoding='utf8') as filecontents:
    data = json.load(filecontents)
for block in data:
    player_first+= block['first_name'].lower().split()
    player_last +=block['last_name'].lower().split()
    player_nick +=block['known_name'].lower().split()


with open('t-SNE figure data.json', 'r', encoding='utf8') as filecontents:
    data = json.load(filecontents)
plt.rc('font', size=4)
for max_x in range(-80, 79, 40):
    for max_y in range(-80, 79, 40):
        plt.figure(num = 1, figsize=(11.7, 8.3))
        plt.scatter([max_x,max_x + 40],[max_y,max_y+40],s=0.001)

        for key in data:
            pos_x = data[key][0]
            pos_y = data[key][1]
            if max_x < pos_x < max_x + 40 and max_y < pos_y < max_y + 40:
                if key in teams:
                    plt.annotate(key, xy=(pos_x, pos_y), xytext=(pos_x, pos_y), color='tab:green')
                elif key in player_first:
                    plt.annotate(key, xy=(pos_x, pos_y), xytext=(pos_x, pos_y), color='tab:purple')
                elif key in player_last:
                    plt.annotate(key, xy=(pos_x, pos_y), xytext=(pos_x, pos_y), color='tab:red')
                elif key in player_nick:
                    plt.annotate(key, xy=(pos_x, pos_y), xytext=(pos_x, pos_y), color='tab:pink')
                elif re.match(r'\w*ed\b', key):
                    plt.annotate(key, xy=(pos_x, pos_y), xytext=(pos_x, pos_y), color='tab:olive')
                elif re.match(r'\w*ing\b', key):
                    plt.annotate(key, xy=(pos_x, pos_y), xytext=(pos_x, pos_y), color='tab:brown')
                else:
                    plt.annotate(key, xy=(pos_x, pos_y), xytext=(pos_x, pos_y), color='tab:blue')
        # plt.scatter(80,80, color='tab:green', label='teams', s= 1)
        # plt.scatter(80,80, color='tab:purple', label='first name', s = 1)
        # plt.scatter(80,80, color='tab:red', label='last name', s = 1)
        # plt.scatter(80,80, color = 'tab:olive', label='passive (-ed)', s = 1)
        # plt.scatter(80,80, color = 'tab:brown', label='active (-ing)', s = 1)
        # plt.scatter(80,80, color = 'tab:blue', label='other', s = 1)
            #
        # plt.figure(figsize=(11.7, 16.6), dpi=300)
        # fig = plt.figure(1, figsize=(11.7, 16.6))
        # ax = fig.add_subplot(111)
        # plt.title('All words from sportsmole commentary, based on word similarity')
        # plt.legend(loc='upper right')
        ax = plt.gca()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['left'].set_visible = False
        ax.spines['bottom'].set_visible = False
        ax.spines['right'].set_visible = False
        ax.spines['top'].set_visibile = False
        # fig = plt.gcf()
        # fig.set_size_inches(8.3, 11.7)
        plt.savefig('t-SNE embedding coloured words ' + str(max_x) + ' ' + str(max_y) + '.pdf', bbox_inches='tight', dpi=150, pad_inches=0.0)
        #  plt.show()
        plt.close()

