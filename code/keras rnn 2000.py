import keras as K
import numpy as np
import time
import json
import load_data
import collections
from nltk import tokenize
from gensim.models import KeyedVectors, word2vec
import re

test = False
print('Testing with generated data, saving disabled' if test else 'Running on commentary data, saving enabled')
config = {'word2vec size': 100, 'batch size': 1, 'print average': 1000, 'save frequency': 10000,
          'export dir': '/Users/Max/Documents/Master Studies/6th term/Master thesis/text creation/tensorflow save/',
          'vocab size': 80}
replacement_dict = {'player first': '<player_first>', 'player last': '<player_last>', 'team': '<team>',
                    'padding': '<padding>', 'end of comment': '<end_of_comment>', 'unknown': '<unk>', 'name': '<name>'}
player_name_files = ['Player names Premier League.txt', 'Player names Bundesliga.txt',
                     'Player names La Liga.txt', 'Player names Ligue 1.txt']

tick = time.time()

team_replacement = ['republic', 'gibraltar', 'ajax', 'brazil', 'chornomorets']
player_replacement = ['riviere']
if test is True:
    word_vectors = {str(_): np.random.rand(config['word2vec size']) for _ in range(80)}
    comment_dict = {str(__): [str(_) for _ in range(np.random.randint(0, 10), np.random.randint(50, config['vocab size']))] for __ in range(601)}
    print('Training data generated, ' + str(time.time() - tick) + ' seconds spent.')
else:
    # raise FileNotFoundError
    with open('processed text.json', 'r', encoding='utf8') as filecontents:
        comment_dict = json.load(filecontents)
    word_vectors = KeyedVectors.load_word2vec_format('word2vec vectors processed.txt', 'word2vec vocabulary processed.txt')
    print('Data loaded')

        # with open('pure_text.json', 'r', encoding='utf8') as filecontents:
        #     comment_dict = json.load(filecontents)
        # teams = []
        # with open('Teams.txt', 'r', encoding='utf8') as filecontents:
        #     for line in filecontents.readline():
        #         teams.append(line.lower())
        # team_names = []
        # for team in teams:
        #     team_names += team.split()
        # with open('Player names Premier League.txt', 'r', encoding='utf8') as filecontents:
        #     names = filecontents.read()
        # with open('Player names La Liga.txt', 'r', encoding='utf8') as filecontents:
        #     names = '\n'.join((names, filecontents.read()))
        # with open('Player names Ligue 1.txt', 'r', encoding='utf8') as filecontents:
        #     names = '\n'.join((names, filecontents.read()))
        # with open('Player names Bundesliga.txt', 'r', encoding='utf8') as filecontents:
        #     names = '\n'.join((names, filecontents.read()))
        # print(names[:200])
        # names = re.sub('\n\w\n', '\n', names, flags=(re.UNICODE|re.MULTILINE|re.IGNORECASE)) # take out A, B…
        # names = re.sub('\(.*?\)\n', '\n', names)
        # names = names.lower().split('\n')
        # player_names = []
        # for name in names:
        #     player_names += name.split(' ')
        # unknowns = []
        # word_count = collections.Counter()
        # print(player_names[:30])
        # for comment in comment_dict:
        #     for counter, word in enumerate(comment_dict[comment]):
        #         word_count[word] += 1
        #         if word in player_names:
        #             comment_dict[comment][counter] = replacement_dict['name']
        #         elif word in team_names:
        #             comment_dict[comment][counter] = replacement_dict['team']
        #     print(comment)
        # for word in word_count:
        #     if word_count[word] <= 5:
        #         unknowns.append(word)
        # for comment in comment_dict:
        #     for counter, word in enumerate(comment_dict[comment]):
        #         if word in unknowns:
        #             comment_dict[comment][counter] = comment_dict['unknown']
        # word_model = word2vec.Word2Vec(comment_dict.values(), size=100)
        # word_model.wv.save_word2vec_format('word2vec vectors processed.txt', 'word2vec vocabulary processed.txt')
        # word_vectors = word_model.wv
        # del word_model
        # with open('processed text.json', 'w+', encoding='utf8') as filecontents:
        #     json.dump(comment_dict, filecontents)
        # print('Word vectors, commentary generated from file, ' + str(time.time() - tick) + ' seconds spent.')
    # except FileNotFoundError or NameError:
    #     print('Regenerating commentary…')
    #     commentary = load_data.load_commentary('sportsmole commentary.json', 'commentary sportsmole')
    #     comments = []
    #     for match in commentary:
    #         comments.append(match[1].lower())
    #
    #     first_name, last_name = load_data.load_player_names(player_name_files)
    #     team_names = load_data.load_team_names(['Teams.txt'])
    #     to_be_replaced_dict = {'player first': first_name, 'player last': last_name, 'team': team_names}
    #
    #     word_count = collections.Counter()
    #     processed_comments = []
    #     for comment in comments:
    #         comment = load_data.name_replace(comment, to_be_replaced_dict, replacement_dict)
    #         processed_comment = tokenize.word_tokenize(comment)
    #         processed_comment += [replacement_dict['end of comment']]
    #         for word in processed_comment:
    #             word_count[word] += 1
    #         processed_comments.append(processed_comment)
    #     del comments
    #     for processed_comment in processed_comments:
    #         for counter, word in enumerate(processed_comment):
    #             if word_count[word] <= 5:
    #                 processed_comment[counter] = replacement_dict['unknown']
    #     comment_dict = {counter: comment for counter, comment in enumerate(processed_comments)}
    #     with open('processed text.json', 'w+', encoding='utf8') as filecontents:
    #         json.dump(comment_dict, filecontents)
    #
    #     time_taken = time.time() - tick
    #     minutes = int(time_taken // 60)
    #     seconds = int(time_taken % 60)
    #     print('All files generated and saved successfully. Time taken: ' + str(minutes) + ' minutes, ' + str(seconds) + ' seconds')

def commentary_generator(comment_dict, word_vectors, batch_size=16, word2vec_size=100):
    number_of_comments = len(comment_dict)
    while True:
        comments = []
        length_list = []
        for _ in range(batch_size):
            comment_nr = np.random.randint(number_of_comments)
            comments.append(comment_dict[str(comment_nr)])
            length_list.append(len(comment_dict[str(comment_nr)]))
        max_length = max(length_list)
        for element in range(batch_size):
            comment = [word_vectors[word] for word in comments[element]]
            comment = np.array(comment).reshape(-1, word2vec_size)
            padding = max_length - length_list[element]
            comment = np.concatenate((comment, np.zeros((padding, word2vec_size))), axis=0)
            comment.reshape(1, -1, word2vec_size)
            comments[element] = comment
        comments = np.array(comments).reshape(batch_size, -1, word2vec_size)
        features = comments[:,:-1,:]
        labels = comments[:,1:,:]
        yield features, labels


def prediction_starter(comment_dict, word_vectors, batch_size=16, word2vec_size=100):
    number_of_comments=len(comment_dict)
    comments = []
    for _ in range(batch_size):
        comment_nr = np.random.randint(number_of_comments)
        comments.append(comment_dict[str(comment_nr)][0])
    comments = np.array([word_vectors[word] for word in comments]).reshape(batch_size, -1, word2vec_size)
    return comments

saving = 'model.hdf5'
batch_size = 16
viewed_comments = 1e5
train = True
try:
    model = K.models.load_model(saving)
except OSError:
    print('Loading error, rebuilding Keras model')
    model = K.models.Sequential()
    model.add(K.layers.LSTM(2000, activation='tanh', return_sequences=True, input_shape=(None, 100)))
    model.add(K.layers.LSTM(100, activation='tanh', return_sequences=True))
    model.compile(optimizer=K.optimizers.RMSprop(lr=0.01), loss=K.losses.cosine_proximity, metrics=['accuracy'])
if train:
    for epoch in range(50):
        model.fit_generator(commentary_generator(comment_dict, word_vectors, batch_size),
                            steps_per_epoch=viewed_comments//batch_size, epochs=1, verbose=2)
        model.save(saving)
        word_list = prediction_starter(comment_dict, word_vectors, batch_size)
        for word in range(10):
            next_word = model.predict_on_batch(word_list)
            word_list = np.concatenate((word_list, next_word[:, -1, :].reshape(batch_size, 1, 100)), axis=1)
        for sentence in word_list:
            real_sentence = [word_vectors.similar_by_vector(word, topn=1) for word in sentence]
            print(real_sentence)
    print('training done')
else:
    while True:
        prompt = 'write your first few words, "end" to finish testing the model.'
        initial = input(prompt).lower().split()
        if initial == 'end':
            break
        vectors = []
        for word in initial:
            try: vectors.append(np.array(word_vectors[word]).reshape(1, 1, 100))
            except KeyError:
                vectors.append(np.array(word_vectors[replacement_dict['unknown']]).reshape(1, 1, 100))
        vectors = np.concatenate(np.array(vectors), axis = 1)
        vectors = np.concatenate([vectors*batch_size], axis=0).reshape(batch_size, -1, 100)
        for additional_words in range(20):
            next_word = model.predict_on_batch(vectors)
            vectors = np.concatenate((vectors, next_word[:,-1, :].reshape(batch_size, 1, 100)), axis=1)
        for sentence in vectors[0,...]:
            real_sentence = [word_vectors.similar_by_vector(word, topn=1) for word in sentence]
            print(real_sentence)
