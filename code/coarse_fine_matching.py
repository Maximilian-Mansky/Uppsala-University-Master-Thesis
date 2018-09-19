# import tensorflow as tf
import numpy as np
import os
import json
from gensim.models import KeyedVectors, word2vec
from nltk import tokenize
import collections
import keras as K
import re

name_path = 'tournament12/season83'
event_path = './tournament12/season83/events'


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def file_names(name_path):
    match_names = [file for file in os.listdir(name_path) if os.path.isfile(os.path.join(name_path, file))]
    # match_descriptions = [os.join('events', file) for file in match_names]
    for counter, value in enumerate(match_names):
        if value == '.DS_Store':
            del match_names[counter]
    name_dict = {}
    for counter, file in enumerate(match_names):
        with open(os.path.join(name_path, file), 'r', encoding='utf8') as filecontents:
            name_dict[counter] = {'name': file, 'contents': json.load(filecontents)}

    identifier = {}
    for counter in name_dict:
        identifier[counter] = {'home team': name_dict[counter]['contents']['matches'][0]['homeTeamName'],
                               'away team': name_dict[counter]['contents']['matches'][0]['awayTeamName'],
                               'match date': name_dict[counter]['contents']['matches'][0]['scheduleStart'].split('T')[0],
                               'file name': name_dict[counter]['name']}
    return name_dict, identifier


name_dict, identifier = file_names(name_path)

def create_connections(name_dict, identifier):
    with open('sportsmole commentary.json', 'r', encoding='utf8') as filecontents:
        sportsmole = json.load(filecontents)
    connections = {}
    for key in sportsmole:
        for counter in name_dict:
            if (sportsmole[key]['home team'] == identifier[counter]['home team'] \
                        and sportsmole[key]['away team'] == identifier[counter]['away team'] \
                        and sportsmole[key]['match date'] == identifier[counter]['match date']) \
                    or (sportsmole[key]['match date'] == identifier[counter]['match date'] \
                                and ((sportsmole[key]['home team'] is None and sportsmole[key]['away team'] == identifier[counter]['away team']) \
                                             or (sportsmole[key]['home team'] == identifier[counter]['home team'] and sportsmole[key]['away team'] is None))):
                connections[key] = {'dict address': counter, 'file address': identifier[counter]['file name']}
    coarse_data = {}

    for key in connections:
        coarse_data[key] = {}
        for time_stamp, comment in sportsmole[key]['commentary sportsmole']:
            coarse_data[key][eval(time_stamp.split()[0])] = tokenize.word_tokenize(comment)
    del sportsmole
    return coarse_data, connections

coarse_data, connections = create_connections(name_dict, identifier)
print(len(coarse_data))


def fine_data_creation(connections, event_path):
    fine_data = {}

    for key in connections:
        fine_data[key] = {}
        with open(os.path.join(event_path, connections[key]['file address']), 'r', encoding='utf8') as filecontents:
            match_fine_grade = json.load(filecontents)
        match_fine_grade_flat = []
        for first_level in match_fine_grade:
            for second_level in first_level:
                match_fine_grade_flat.append(second_level)
                assert type(second_level) == type({'this is': 'a dict'})
        carrier = {}
        goal = 0
        for block in match_fine_grade_flat:
            minute = block['min']
            if block['description'] == 'Goal':
                goal += 1
            try:
                carrier[str(minute)]['x list'].append(block['x'])
                carrier[str(minute)]['y list'].append(block['y'])
                carrier[str(minute)]['goal'].append(goal)
                goal = 0
            except KeyError:
                carrier[str(minute)] = {'x list': [block['x']], 'y list': [block['y']], 'goal': [goal]}
                goal = 0
        fine_data[key] = carrier
        # print('flat list length', len(match_fine_grade_flat), 'fine data length', len(fine_data[key]))
        # raise ValueError
    return fine_data


# name_dict, identifier = file_names(name_path)
# coarse_data, connections = create_connections(name_dict, identifier)

# fine_data = fine_data_creation(connections, event_path)
# try:
#     with open('fine data.json', 'r', encoding='utf8') as filecontents:
#         fine_data = json.load(filecontents)
#     with open('coarse data.json', 'r', encoding='utf8') as filecontents:
#         coarse_data = json.load(filecontents)
#     # name_dict, identifier = file_names(name_path)
#     # coarse_data, connections = create_connections(name_dict, identifier)
#     # with open('coarse data.json', 'w', encoding='utf8') as filecontents:
#     #     json.dump(coarse_data, filecontents)
#     print('loading prior files…')
# except FileNotFoundError:
#     print('recreating files…')
#     name_dict, identifier = file_names(name_path)
#     coarse_data, connections = create_connections(name_dict, identifier)
#     fine_data = fine_data_creation(connections, event_path)
#     with open('fine data.json', 'w+', encoding='utf8') as filecontents:
#         json.dump(fine_data, filecontents)
#     with open('coarse data.json', 'w+', encoding='utf8') as filecontents:
#         json.dump(coarse_data, filecontents, cls=NumpyEncoder)
#     print('json files written')
#
# with open('all players PL.txt', 'r', encoding='utf8') as filecontents:
#     text = filecontents.read()
# lines = text.split('\n')
# names = []
# clubs = []
# for line in lines:
#     if re.match('[0-9]+\.\t', line):
#         _, name, club, _ = line.split('\t')
#         names.append(name.lower())
#         clubs.append(club.lower())
# clubs = list(set(clubs))
# club_list = []
# for club in clubs:
#     club_list += club.split(' ')
# individuals = []
# for name in names:
#     individuals += name.split(' ')
# word_count = collections.Counter()
# sentences = []
# for match in coarse_data:
#     for minute in coarse_data[match]:
#         for counter, word in enumerate(coarse_data[match][minute]):
#             if word in individuals:
#                 coarse_data[match][minute][counter] = '<player>'
#             elif word in club_list:
#                 coarse_data[match][minute][counter] = '<team>'
#             word_count[word] += 1
#         sentences.append(coarse_data[match][minute])
# with open('coarse data replaced.json', 'w+', encoding='utf8') as filecontents:
#     json.dump(coarse_data, filecontents)
#
# for sent_count, sentence in enumerate(sentences):
#     for w_count, word in enumerate(sentence):
#         if word_count[word] <= 5:
#             sentences[sent_count][w_count] = '<unk>'
# word_vectors = word2vec.Word2Vec(sentences)
# word_vectors.wv.save_word2vec_format('wv small processed.txt')


# wv_size = 100
#
# with open('coarse data replaced.json', 'r', encoding='utf8') as filecontents:
#     coarse_data = json.load(filecontents)
# with open('fine data.json', 'r', encoding='utf8') as filecontents:
#     fine_data = json.load(filecontents)
# sentences = []
# for match in coarse_data:
#     for minute in coarse_data[match]:
#         for counter, word in enumerate(coarse_data[match][minute]):
#         #     # if word in individuals:
#         #     #     coarse_data[match][minute][counter] = '<player>'
#         #     # elif word in club_list:
#         #     #     coarse_data[match][minute][counter] = '<team>'
#             if word in ['gundogan']:
#                 coarse_data[match][minute][counter] = '<player>'
#         sentences.append([word.lower() for word in coarse_data[match][minute]])
#
# # coarse_data = coarse_lower
#
# with open('coarse data replaced.json', 'w', encoding='utf8') as filecontents:
#     json.dump(coarse_data, filecontents)
# word_vectors = word2vec.Word2Vec(sentences, size=wv_size)
# print(word_vectors.wv.most_similar(positive='goal', topn=20))
# # word_vectors = KeyedVectors.load_word2vec_format('wv small processed.txt')
#
# # match LSTM to vector
#
# def input_data_generator(feature_data, label_data, word_vectors, predict = False, with_goal=False):
#     goals = {}
#     for match in feature_data:
#         goals[match] = {}
#         goal_found = False
#         for minute_selection in feature_data[match]:
#             if max(feature_data[match][minute_selection]['goal']):
#                 goals[match][minute_selection] = {}
#                 goals[match][minute_selection]['x list'] = feature_data[match][minute_selection]['x list']
#                 goals[match][minute_selection]['y list'] = feature_data[match][minute_selection]['y list']
#                 goals[match][minute_selection]['goal'] = feature_data[match][minute_selection]['goal']
#                 goal_found=True
#         if not goal_found:
#             del goals[match]
#     while True:
#         if np.random.randint(0, 2):
#             match = np.random.choice(list(goals.keys()))
#             minute = np.random.choice(list(goals[match].keys()))
#             x_pos = np.array(goals[match][minute]['x list']).reshape(1, -1, 1) / 100
#             y_pos = np.array(goals[match][minute]['y list']).reshape(1, -1, 1) / 100
#             goal = np.array(goals[match][minute]['goal']).reshape(1, -1, 1)
#             if with_goal:
#                 feature = np.concatenate((x_pos, y_pos, goal), axis=2)
#             else:
#                 feature = np.concatenate((x_pos, y_pos), axis=2)
#             label = np.array(word_vectors['goal']).reshape(1, wv_size)
#         else:
#             match = np.random.choice(list(label_data.keys()))
#             minute = np.random.choice(list(label_data[match].keys()))
#             word = label_data[match][minute][0].lower()
#             try:
#                 label = np.array(word_vectors[word]).reshape(1, wv_size)
#             except KeyError: # word not found
#                 label = np.array(word_vectors['<unk>']).reshape(1, wv_size)
#             try:
#                 x_pos = np.array(feature_data[match][minute]['x list']).reshape(1, -1, 1) / 100
#                 y_pos = np.array(feature_data[match][minute]['y list']).reshape(1, -1, 1) / 100
#                 goal = np.array(feature_data[match][minute]['goal']).reshape(1, -1, 1)
#             except KeyError: # timewise mismatch; take the time block just before
#                 possible_minutes = np.array([int(minute) for minute in feature_data[match].keys()]) - int(minute)
#                 closest = np.nonzero(possible_minutes < 0)
#                 closes_minute = possible_minutes[closest][-1] + int(minute)
#                 x_pos = np.array(feature_data[match][str(closes_minute)]['x list']).reshape(1, -1, 1) / 100
#                 y_pos = np.array(feature_data[match][str(closes_minute)]['y list']).reshape(1, -1, 1) / 100
#                 goal = np.array(feature_data[match][str(closes_minute)]['goal']).reshape(1, -1, 1)
#             if with_goal:
#                 feature = np.concatenate((x_pos, y_pos, goal), axis=2)
#             else:
#                 feature = np.concatenate((x_pos, y_pos), axis=2)
#         if not predict:
#             yield feature, label
#         else:
#             # print(goal[0,-1,:])
#             yield feature
#
#
# with_goal = True
#
#
# model = K.Sequential()
# model.add(K.layers.LSTM(wv_size, activation='tanh', batch_input_shape=(1, None, 3 if with_goal else 2), return_sequences=False))
# model.add(K.layers.Dense(wv_size, activation='tanh'))
# model.add(K.layers.Dense(wv_size, activation='tanh'))
# model.compile(optimizer=K.optimizers.RMSprop(lr=0.07), loss=K.losses.cosine_proximity, metrics=[K.metrics.mean_squared_error])
# model.fit_generator(input_data_generator(fine_data, coarse_data, word_vectors, with_goal=with_goal), steps_per_epoch=256, epochs=40, verbose=2)
# prediction_batch = []
# for _ in range(10):
#     prediction_batch.append(model.predict_generator(input_data_generator(fine_data, coarse_data, word_vectors, predict=True, with_goal=with_goal), steps=1))
# for block in prediction_batch:
#     print(word_vectors.similar_by_vector(block.reshape(wv_size,)))

