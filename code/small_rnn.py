import keras as K
import json
import collections
import numpy as np
import matplotlib.pyplot as plt

with open('coarse data replaced.json', 'r', encoding='utf8') as filecontents:
    coarse_data = json.load(filecontents)

sentences = []
word_count = collections.Counter()

for match in coarse_data:
    for minute in coarse_data[match]:
        sentences.append(coarse_data[match][minute])
        for word in coarse_data[match][minute]:
            if word in ['mourinho']:
                word_count['<player>'] += 1
            else:
                word_count[word] += 1

unknownness = 3

for s_count, sentence in enumerate(sentences):
    for w_count, word in enumerate(sentence):
        if word_count[word] <= unknownness:
            sentences[s_count][w_count] = '<unk>'

unknowns = []
for word in word_count:
    if word_count[word] <= unknownness:
        word_count['<unk>'] += word_count[word]
        unknowns.append(word)
for word in unknowns:
    del word_count[word]

# reserve 0 as padding
word_to_index = {word: index + 1 for index, (word, _) in enumerate(word_count.most_common())}
index_to_word = {index + 1: word for index, (word, _) in enumerate(word_count.most_common())}
word_to_index['<eos>'] = len(index_to_word) + 1
index_to_word[len(word_to_index)] = '<eos>'
index_to_word[0] = '<pad>'


def input_generator(sentences, batch_size, vocab_size, predict=False):
    counter = 0
    while True:
        index_sequences = []
        lengths = []
        for _ in range(batch_size):
            sentence = sentences[counter % len(sentences)]
            lengths.append(len(sentence))
            index_sequence = np.array([word_to_index[word] for word in sentence]).reshape(1, -1, 1)
            index_sequences.append(index_sequence)
            counter += 1
        max_length = max(lengths)
        label_sequences = []
        for counter, index_sequence in enumerate(index_sequences):
            index_sequence = np.concatenate((index_sequence, np.zeros((1, max_length - lengths[counter], 1), dtype=np.int32)), axis=1)
            index_sequences[counter] = index_sequence
            label_sequence = np.zeros((1, max_length, vocab_size), dtype=np.int32)
            for index in range(max_length):
                label_sequence[0, index, index_sequence[0, index, 0]] = 1
            label_sequences.append(label_sequence)
        features = np.concatenate(index_sequences, axis=0)
        labels = np.concatenate(label_sequences, axis=0)
        yield features[:, :-1, :] if predict else features[:, 0:-1, :], labels[:, 1:, :]


batch_size = 16
vocab_size = len(index_to_word)
training = False
examine = False
assessed = 2
try:
    model = K.models.load_model('ssmall model.h5')
    print('model loaded')
    # raise OSError
except OSError:
    print('retraining model')
    model = K.Sequential()
    model.add(K.layers.LSTM(200, batch_input_shape=(batch_size, None, 1), return_sequences=True, stateful=True))
    model.add(K.layers.Dense(vocab_size, activation='softmax'))
    model.compile(optimizer=K.optimizers.Adam(), loss=K.losses.categorical_crossentropy, metrics=['accuracy'])
    history = model.fit_generator(input_generator(sentences, batch_size, vocab_size), steps_per_epoch=128, epochs=20)
    model.save('ssmall model.h5')
    plt.plot(history.history['loss'], label='loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Fitting loss of the small neural network')
    plt.legend(loc='upper right')
    plt.savefig('fitting loss.pdf', dpi=600, transparent=True, bbox_inches='tight')
    plt.show()

if training:
    # extra training step for creating initial context vector
    model.fit_generator(input_generator(sentences, batch_size, vocab_size), steps_per_epoch=128, epochs=1)
    # model.save('small model.h5')
sentence_in = np.random.choice(sentences)
print(' '.join(sentence_in))


if examine:
    for counter in range(0, 160, batch_size):
        index_sequences = [[word_to_index[word] for word in sentences[counter%len(sentences)]]]
        # length_list = [len(index_sequences)]
        for filler in range(1, batch_size):
            index_sequences.append([word_to_index[word] for word in sentences[counter%len(sentences) + filler]])
            # length_list.append(len(index_sequences[-1]))
        length_list = [len(index_sequence) for index_sequence in index_sequences]
        max_length = max(length_list)
        assert len(index_sequences) == batch_size
        for seq_count, sequence in enumerate(index_sequences):
            index_sequences[seq_count] = np.concatenate((np.array(sequence, dtype=np.int32).reshape(1, -1, 1), np.zeros((1, max_length - length_list[seq_count], 1), dtype=np.int32)), axis=1)
        # [print(index_sequence.shape[1]) for index_sequence in index_sequences]
        index_sequences = np.concatenate(index_sequences, axis=0)
        new_sequences = model.predict_on_batch(index_sequences)
        print(counter)
        print([index for index in index_sequences[0,:,0]])
        new_sequence = new_sequences[0]
        # print(np.argmax(new_sequence, axis=1))
        # new_index = [np.argmax(one_hot) for one_hot in new_sequence.flatten()]
        print([index for index in np.argmax(new_sequence, axis=1)])

    accuracy = model.evaluate_generator(input_generator(sentences, batch_size, vocab_size, predict=True), steps=50)
    print(accuracy)


    predictions = model.predict(np.array([word_to_index[word] for word in sentence_in] * batch_size).reshape(batch_size, -1, 1))
    print('sentence to sentence accuracy')
    for prediction in predictions:
        sentence = [np.argmax(one_hot) for one_hot in prediction * 10]
        if examine:
            print('Output sequence:', sentence)
            print('number of words', len(index_to_word))
            # print([np.nonzero(one_hot > 0.3) for one_hot in prediction])
            # for counter, one_hot in enumerate(prediction):
            #     if counter < assessed:
            #         plt.plot(one_hot, label='word #' + str(counter))
            examine = False
            print(' '.join([index_to_word[index] for index in sentence]))
        for counter, word in enumerate([index_to_word[index] for index in sentence]):
            print(sentence_in[counter] + ' & ' + word + '\\\\')
    plt.legend(loc='upper right')
    plt.show()

    print('prediction based on initial word')
    for counter in range(10):
        test_sentences = np.random.choice(sentences, batch_size)
        initial_words = [sentence[0] for sentence in test_sentences]
        initials = np.array([word_to_index[word] for word in initial_words]).reshape(batch_size, 1, 1)
        for words in range(20):
            prediction = model.predict_on_batch(initials)
            next_index = np.array([[np.argmax(one_hot) for one_hot in next_word] for next_word in prediction]).reshape(batch_size, -1, 1)
            # print(initials.shape, next_index.shape)
            initials = np.concatenate((initials, next_index[:,-1, :].reshape(batch_size, 1, 1)), axis=1)
        for initial in initials:
            print(' '.join([index_to_word[index] for index in initial.flatten()]))
