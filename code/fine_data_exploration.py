import keras as K
import numpy as np
import json
import os
import matplotlib.pyplot as plt

sportsmole_green = 69/255, 125/255, 20/255
goal_blue = 0, 100/255, 163/255


try:
    with open('collected possession chains.json', 'r', encoding='utf8') as filecontents:
        contents = json.load(filecontents)
    chains = contents['chains']
    index_numbers = contents['indices']
    print('possession chain loaded')
except FileNotFoundError:
    print('possession chains recreation started')
    index_numbers = {'other': [], 'Goal': [], 'Throw-in Taken': [], 'Corner Taken': []}
    name_path = './tournament12/season83/events'
    files = [os.path.join(name_path, file) for file in os.listdir(name_path) if os.path.isfile(os.path.join(name_path, file))]
    del files[-1]
    chains = []
    counter = 0
    for file in files:
        with open(file, 'r', encoding='utf8') as filecontents:
            match = json.load(filecontents)
        for possession_chain in match:
            x_list = []
            y_list = []
            description = 'other'
            for block in possession_chain:
                x_list.append(block['x'])
                y_list.append(block['y'])
                try:
                    if block['description'] in ['Goal', 'Throw-in Taken', 'Corner Taken']:
                        description = block['description']
                except KeyError:
                    pass
            index_numbers[description].append(counter)
            chains.append({'x': x_list, 'y': y_list, 'description': description})
            counter += 1

    with open('collected possession chains.json', 'w+', encoding='utf8') as filecontents:
        json.dump({'chains': chains, 'indices': index_numbers}, filecontents)
    print('possession chains saved to file')

one_hot_matching = {'Goal': np.array([1, 0, 0, 0]).reshape(1, 4), 'Throw-in Taken': np.array([0, 1, 0, 0]).reshape(1, 4),
                    'Corner Taken': np.array([0, 0, 1, 0]).reshape(1, 4), 'other': np.array([0, 0, 0, 1]).reshape(1, 4)}


def input_generator(chains, indices, batch_size=16, focus_on=None, training = True):
    if focus_on is not None:
        possible_outcomes = focus_on
    else:
        possible_outcomes = list(indices.keys())
    while True:
        features = []
        labels = []
        length_list = []
        for _ in range(batch_size):
            descriptor = np.random.choice(possible_outcomes)
            chain_number = np.random.choice(indices[descriptor])
            possession_chain = chains[chain_number]
            x_list = np.array(possession_chain['x']).reshape(1, -1, 1)
            y_list = np.array(possession_chain['y']).reshape(1, -1, 1)
            feature = np.concatenate((x_list, y_list), axis=2)
            label = one_hot_matching[possession_chain['description']]
            features.append(feature)
            labels.append(label)
            length_list.append(feature.shape[1])
        max_length = max(length_list)
        for counter, feature in enumerate(features):
            features[counter] = np.concatenate((np.zeros((1, max_length - length_list[counter], 2)), feature), axis=1)
        features = np.concatenate(features, axis=0)
        labels = np.concatenate(labels, axis=0)
        if training:
            yield features, labels
        else:
            yield features


def scoring(chains, indices, selection, batch_size=16):
    goal_selection = np.random.choice(index_numbers[selection], batch_size)
    features = []
    labels = []
    length_list = []
    for goal_chain in goal_selection:
        goal_x = np.array(chains[goal_chain]['x']).reshape(1, -1, 1)
        goal_y = np.array(chains[goal_chain]['y']).reshape(1, -1, 1)
        feature = np.concatenate((goal_x, goal_y), axis=2)
        label = one_hot_matching[selection]
        length_list.append(feature.shape[1])
        features.append(feature)
        labels.append(label)
    max_len = max(length_list)
    for counter, feature in enumerate(features):
        features[counter] = np.concatenate((np.zeros((1, max_len - length_list[counter], 2)), feature), axis=1)
    features = np.concatenate(features, axis=0)
    labels = np.concatenate(labels, axis=0)
    return features


batch_size = 16
focus_on = 'Corner Taken'

try:
    model = K.models.load_model('goal fitting model.h5')
except OSError:
    model = K.models.Sequential()
    model.add(K.layers.LSTM(15, batch_input_shape=(batch_size, None, 2), return_sequences=False))
    model.add(K.layers.Dense(10, activation='tanh'))
    model.add(K.layers.Dense(len(one_hot_matching), activation='softmax'))
    model.compile(optimizer=K.optimizers.RMSprop(lr=0.005), loss=K.losses.categorical_crossentropy)
    model.fit_generator(input_generator(chains, index_numbers, batch_size), steps_per_epoch=128, epochs=8) # general training
    model.save('goal fitting model.h5')


# for prediction in  ['Goal', 'Throw-in Taken', 'Corner Taken', 'other']:
#     correct = 0
#     wrong = 0
#     for counter in range(10):
#         goal_score = model.predict_generator(input_generator(chains, index_numbers, batch_size, focus_on=[prediction], training=False), steps=1)
#         for scoring in goal_score:
#             # print(scoring.flatten())
#             if np.argmax(scoring.flatten()) == ['Goal', 'Throw-in Taken', 'Corner Taken', 'other'].index(prediction):
#                 correct += 1
#             else:
#                 wrong += 1
#     print(prediction)
#     print(correct / (correct + wrong))
#     print(wrong / (correct + wrong))

im_count = 0
color_wheel = {'Goal': (1, 0, 0), 'Throw-in Taken': goal_blue, 'Corner Taken': sportsmole_green, 'other': (0,0,0)}
plt_label = True
fig, axes = plt.subplots(figsize=(6*0.8, 4*0.8))

for prediction in ['Goal', 'Throw-in Taken', 'Corner Taken', 'other']:
    features = []
    # labels = []
    length_list = []
    for chain_number in index_numbers[prediction]:
        possession_chain = chains[chain_number]
        x_list = np.array(possession_chain['x']).reshape(1, -1, 1)
        y_list = np.array(possession_chain['y']).reshape(1, -1, 1)
        feature = np.concatenate((x_list, y_list), axis=2)
        # label = one_hot_matching[possession_chain['description']]
        features.append(feature)
        # labels.append(label)
        length_list.append(feature.shape[1])
        max_length = max(length_list)
        if len(features) == batch_size:
            for counter, feature in enumerate(features):
                features[counter] = np.concatenate((np.zeros((1, max_length - length_list[counter], 2)), feature), axis=1)
            features = np.concatenate(features, axis=0)
            result = model.predict_on_batch(features)
            for counter, score in enumerate(result):
                answer = np.argmax(score.flatten())
                if not answer == ['Goal', 'Throw-in Taken', 'Corner Taken', 'other'].index(prediction):
                    chain = features[counter]
                    x_list, y_list = np.split(chain, 2, axis=1)
                    x_list = x_list.flatten() * 6 / 4
                    y_list = y_list.flatten()
                    zeros = 0
                    for element in x_list:
                        if element == 0:
                            zeros += 1
                        else:
                            break
                    plt.plot(x_list[zeros:], y_list[zeros:], color=color_wheel[prediction], label=prediction if plt_label else None)
                    plt_label = False
                    im_count += 1
            features = []
            length_list = []
        # if im_count >= 10:
        #     im_count = 0
    plt_label = True
            # break
plt.title('Misclassified possession chains')
plt.xlabel('Ball position along field')
plt.ylabel('Ball position across field')
plt.xticks([])
plt.yticks([])
box = axes.get_position()
axes.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

# Put a legend below current axis
axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
plt.savefig('misclassified_chains.pdf',dpi=600, transparent=True, bbox_inches='tight')
plt.show()