import numpy as np
import matplotlib.pyplot as plt

# name_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'j', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u']
# connection_matrix = np.random.rand(len(name_list),len(name_list))
# connection_matrix += connection_matrix.T
# connection_matrix *= 0.5
#
# alpha = 0.01
# number_of_steps = 50


def distance_builder(connection_matrix, name_list, number_of_steps, learning_rate=0.1, intermediary_pictures=False):
    epsilon = 0.00005 * learning_rate
    position_matrix = np.random.rand(len(name_list), 2)
    momentum_matrix = np.zeros((len(name_list), 2))
    new_quality = 10
    for steps in range(number_of_steps):
        quality = 0
        for counter_base, entity_base in enumerate(name_list):
            momentum_matrix[counter_base] *= 0
            for counter_connect, entity_connect in enumerate(name_list):
                importance = connection_matrix[counter_base, counter_connect]
                desired_distance = 1 - importance
                current_direction = position_matrix[counter_base] - position_matrix[counter_connect]
                current_distance = np.linalg.norm(current_direction)
                direction = learning_rate * np.power(desired_distance - current_distance, 3) * current_direction * abs(importance+0.1) ** 2
                quality -= np.linalg.norm(direction)
                momentum_matrix[counter_base] += direction
        position_matrix += momentum_matrix
        if quality - epsilon < new_quality < quality + epsilon:
            break
        new_quality = quality
        if steps % 50 == 0:
            print(quality)
            if intermediary_pictures:
                show_picture(name_list, position_matrix, connection_matrix, quality)
    return position_matrix, connection_matrix, quality


def show_picture(name_list, position_matrix, connection_matrix, quality):
    for counter_base, entity_base in enumerate(name_list):
        plt.scatter(position_matrix[counter_base][0], position_matrix[counter_base][1], s=100,zorder=2)
        plt.annotate(entity_base.capitalize(),
                     xy=(position_matrix[counter_base][0], position_matrix[counter_base][1]),
                     xytext=(position_matrix[counter_base][0], position_matrix[counter_base][1]), zorder=3)
        for counter_connection, entity_connection in enumerate(name_list):
            colour = connection_matrix[counter_base, counter_connection]
            plt.plot([position_matrix[counter_base][0], position_matrix[counter_connection][0]],
                     [position_matrix[counter_base][1], position_matrix[counter_connection][1]],
                     linewidth = 0.5 * colour,
                     color=(colour, colour, colour), zorder=1)
    plt.title('quality: ' + str(quality))
    plt.show()
    return 0

def circle_rank(central_word, connected_words):
    hfont = {'fontname': 'Helvetica', 'size': 14, 'weight': 'bold'}
    axes = plt.subplot(111, projection='polar')
    angle_number = len(connected_words)
    for counter, (key, similarity) in enumerate(connected_words):
        angle = (2 * np.pi * counter + 1) / angle_number
        distance = 1-similarity
        plt.plot([0,angle], [0, distance], color='k', linewidth = 0.5, zorder=1)
        plt.scatter(angle, distance, s=(600 * similarity ** 2), zorder=2)
        plt.annotate(key.capitalize(), xy=(angle + 0.047, distance), xytext=(angle + 0.047, distance+0.002), **hfont,zorder=3)
        # plt.annotate(str(key[1])[:5], xy = (angle + 0.047, distance/2), xytext=(angle + 0.047, distance / 2))
    plt.scatter(0,0, s=1000, zorder=2)
    plt.annotate(central_word.capitalize(), xy=(0,0), xytext=(0,0), **hfont,zorder=3)
    plt.title('Word2Vec similarity across all sportsmole commentary for "' + str(central_word) + '"')
    plt.annotate('Distance indicates similarity,\nAngle indicates Rank', textcoords='figure fraction', xy=(0.9,0.9), xytext=(0.9,0.9))
    axes.set_xticks([])
    axes.set_yticks([])
    axes.grid(False)
    plt.show()
