import numpy as np
import keras as K
import csv


def read_data(filename):
    data_block = []
    with open(filename, 'r') as filecontents:
        csv_file = csv.reader(filecontents)
        for line in csv_file:
            data_block.append(line)
    for counter, line in enumerate(data_block):
        data_block[counter] = line[:-1]
    return np.array(data_block[1:], dtype=np.float32)


epsilon = 1e-6


def true_pos(y_true, y_pred):
    y_pred_pos = K.backend.round(K.backend.clip(y_pred, 0, 1))
    y_pos = K.backend.round(K.backend.clip(y_true, 0, 1))
    tp = K.backend.sum(y_pos * y_pred_pos) / (K.backend.sum(y_pos) + epsilon)
    return tp


def true_neg(y_true, y_pred):
    y_pred_pos = K.backend.round(K.backend.clip(y_pred, 0, 1))
    y_pred_neg = 1 - y_pred_pos
    y_pos = K.backend.round(K.backend.clip(y_true, 0, 1))
    y_neg = 1 - y_pos
    tn = K.backend.sum(y_neg * y_pred_neg) / (K.backend.sum(y_neg) + epsilon)
    return tn


def false_pos(y_true, y_pred):
    y_pred_pos = K.backend.round(K.backend.clip(y_pred, 0, 1))
    y_pos = K.backend.round(K.backend.clip(y_true, 0, 1))
    y_neg = 1 - y_pos
    fp = K.backend.sum(y_neg * y_pred_pos) / (K.backend.sum(y_neg) + epsilon)
    return fp


def false_neg(y_true, y_pred):
    y_pred_pos = K.backend.round(K.backend.clip(y_pred, 0, 1))
    y_pred_neg = 1 - y_pred_pos
    y_pos = K.backend.round(K.backend.clip(y_true, 0, 1))
    fn = K.backend.sum(y_pos * y_pred_neg) / (K.backend.sum(y_pos) + epsilon)
    return fn


features = read_data('features.csv')
print('readin:', features.shape)
features, labels = np.array_split(features, [8], axis=1)
features = 1- 2 * features / np.max(features, axis=1, keepdims=True)
# indices
goals = np.nonzero(labels == 1)[0]
not_goals = np.nonzero(labels == 0)[0]
# reform to two one-hots
labels = [[1, 0] if goal else [0, 1] for goal in np.squeeze(labels)]
labels = np.array(labels, dtype=np.float32)
goals_choice = np.random.choice(not_goals, 250)
test_indices = np.concatenate((goals, goals_choice))
np.random.shuffle(test_indices)
reduced_features = features[test_indices]
reduced_labels = labels[test_indices]

# labels = read_data('labels.csv')
# labels = labels / np.linalg.norm(labels, axis=0, keepdims=True)
test_indices = np.random.choice(len(features), 1024, replace=False)
features_test = features[test_indices]
labels_test = labels[test_indices]
# print('number of goals: ', np.sum(labels))

activation = 'tanh'
model = K.models.Sequential()
model.add(K.layers.Dense(32, input_shape=(8,), activation='relu', bias_initializer='ones'))
# model.add(K.layers.Dense(64, activation=activation))
# model.add(K.layers.Dense(32, activation=activation))
model.add(K.layers.Dense(16, activation=activation))
model.add(K.layers.Dense(16, activation=activation))
model.add(K.layers.Dense(16, activation=activation))
model.add(K.layers.Dense(8, activation=activation))
model.add(K.layers.Dense(2, activation='softmax'))
model.compile(optimizer=K.optimizers.SGD(lr=0.01), loss=K.losses.categorical_crossentropy, metrics=[true_pos, false_pos, false_neg, true_neg])
model.fit(reduced_features, reduced_labels, epochs=20, batch_size=16, shuffle=True)
score = model.evaluate(features, labels, batch_size=128)
print(score)
###testing###
pos_scoring = np.eye(8, dtype=np.float32)
neg_scoring = - np.eye(8, dtype=np.float32)
scoring = np.concatenate((pos_scoring, neg_scoring), axis=0)
predictions = model.predict(scoring, batch_size=1)
# print(predictions)
