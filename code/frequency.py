import json
import numpy as np
import nltk
import matplotlib.pyplot as plt
import collections

def commentary_counter(file, commentary_name, league = None):
    word_count = collections.Counter()
    with open(file, 'r', encoding='utf8') as filecontents:
        commentary = json.load(filecontents)
    comment_list = []
    comment_length = collections.Counter()
    max_length = 0
    for match in commentary:
        try:
            if commentary[match]['league title'] == league or league is None:
                for comment in commentary[match][commentary_name]:
                    sentence = comment[1]
                    words = nltk.tokenize.word_tokenize(sentence.lower())
                    comment_list.append(words)
                    comment_length[len(words)] += 1
                    max_length = max(max_length, len(words))
                    for word in words:
                        word_count[word] += 1
        except KeyError:
            continue
    del commentary
    # new_filename = file.split('.')[0] + ' comment count.json'
    # with open(new_filename, 'w+', encoding='utf8') as filecontents:
    #     json.dump(comment_length ,filecontents)
    return comment_length, max_length, word_count

try:
    with open('commentary length.json', 'r', encoding='utf8') as filecontents:
        data = json.load(filecontents)
        sm_comment_length = collections.Counter()
        for key in data['sportsmole']:
            sm_comment_length[int(key)] = data['sportsmole'][key]
        g_comment_length = collections.Counter()
        for key in data['goal complete']:
            g_comment_length[int(key)] = data['goal complete'][key]
        h_comment_length = collections.Counter()
        for key in data['goal human']:
            h_comment_length[int(key)] = data['goal human'][key]
        sm_word_count = collections.Counter()
        for key in data['sm words']:
            sm_word_count[key] = data['sm words'][key]
        g_word_count = collections.Counter()
        for key in data['goal complete words']:
            g_word_count[key] = data['goal complete words'][key]
        h_word_count = collections.Counter()
        for key in data['goal human words']:
            h_word_count[key] = data['goal human words'][key]
except FileNotFoundError:
    sm_comment_length, sm_max_length, sm_word_count = commentary_counter('sportsmole commentary.json', 'commentary sportsmole')
    g_comment_length, g_max_length, g_word_count = commentary_counter('goal_com commentary.json', 'commentary goal.com')
    h_comment_length, h_max_length, h_word_count = commentary_counter('goal_com commentary.json', 'commentary goal.com', 'Premier League')
    with open('commentary length.json', 'w+', encoding='utf8') as filecontents:
        json.dump({'sportsmole': sm_comment_length, 'goal complete': g_comment_length, 'goal human': h_comment_length,
                   'sm words': sm_word_count, 'goal complete words': g_word_count, 'goal human words': h_word_count}, filecontents)
# for length in h_comment_length:
#     g_comment_length[length] -= h_comment_length[length]
# s_max = max([int(key) for key in sm_comment_length.keys()])
# g_max = max([int(key) for key in g_comment_length.keys()])
# h_max = max([int(key) for key in h_comment_length.keys()])
# maxmax = max(s_max, g_max, h_max)
# s_plot = []
# g_plot = []
# h_plot = []
# with open('comment_length_detail.csv', 'w+', encoding='utf8') as filecontents:
#     for counter in range(maxmax):
#         s_plot.append(sm_comment_length[counter] / sum(sm_comment_length.values()))
#         g_plot.append(g_comment_length[counter] / sum(g_comment_length.values()))
#         h_plot.append(h_comment_length[counter] / sum(h_comment_length.values()))
#         filecontents.write(str(counter) + ', ' + str(s_plot[counter]) + ', ' + str(h_plot[counter]) + ', ' + str(g_plot[counter]) + '\n')
# plt.plot(s_plot, label='sportsmole commentary')
# plt.plot(g_plot, label='goal.com machine commentary')
# plt.plot(h_plot, label='goal.com human commentary')
# plt.legend(loc='upper right')
# plt.title('commentary length')
# plt.show()
#
s_max_count = max(sm_word_count.values())
for word in h_word_count:
    g_word_count[word] -= h_word_count[word]
g_max_count = max(g_word_count.values())
h_max_count = max(h_word_count.values())
sm_word_count = [sm_word_count[word] / s_max_count for word in sm_word_count]
g_word_count = [g_word_count[word] / g_max_count for word in g_word_count]
h_word_count = [h_word_count[word] / h_max_count for word in h_word_count]
max_count = max(sm_word_count + g_word_count + h_word_count)
min_count = max(min(sm_word_count + g_word_count + h_word_count), 0.00001)

values_s, bins, _ = plt.hist(sm_word_count, np.geomspace(min_count, max_count, 50), label='sportsmole', histtype='step')
values_g, bins, _ = plt.hist(g_word_count, np.geomspace(min_count, max_count, 50), label='goal.com machine', histtype='step')
values_h, bins, _ = plt.hist(h_word_count, np.geomspace(min_count, max_count, 50), label='goal.com human', histtype='step')
sum_s = sum(values_s)
sum_g = sum(values_g)
sum_h = sum(values_h)
plt.title('word frequency')
plt.xlabel('number of words')
plt.ylabel('word frequency')
plt.legend(loc='upper right')
plt.xscale('log')
plt.yscale('log')
plt.show()
with open('word_distribution_full.csv', 'w+', encoding='utf8') as filecontents:
    for counter in range(49):
        filecontents.write(str(bins[counter]) + ', ' + str(values_s[counter] / sum_s) + ', '+ str(values_h[counter]/ sum_h) + ', ' + str(values_g[counter] / sum_g) + '\n')

    # sm_max_count = max(sm_word_count.values())
    # g_max_count = max(g_word_count.values())
    # h_max_count = max(h_word_count.values())
    # max_count = max(sm_max_count, g_max_count, h_max_count)
    # sm_word_count = [sm_word_count[word] / sm_max_count for word in sm_word_count]
    # g_word_count = [g_word_count[word] / g_max_count for word in g_word_count]
#
#     with open('word counts.json', 'w+', encoding='utf8') as filecontents:
#         json.dump({'sportsmole count': sm_word_count, 'goal count': g_word_count}, filecontents)
#
# max_count = max(sm_word_count + g_word_count)
# min_count = min(sm_word_count + g_word_count)
#
#
# sm_bins = plt.hist(sm_word_count, np.geomspace(min_count, max_count, 50), label='sportsmole', histtype='step')
# g_bins = plt.hist(g_word_count, np.geomspace(min_count, max_count, 50), label='goal.com', histtype='step')
# # print(sm_bins)

# x_values = np.geomspace(min_count, max_count, 50)
# with open('word_frequency_bins.csv', 'w+', encoding='utf8') as filecontents:
#     for counter in range(len(sm_bins[0])):
#         filecontents.write(str(x_values[counter]) + ', ' + str(sm_bins[0][counter] / np.sum(sm_bins[0]) if not sm_bins[0][counter] == 0.0 else 'NaN') + ', '
#                            + str(g_bins[0][counter] / np.sum(g_bins[0]) if not g_bins[0][counter] == 0.0 else 'NaN') + '\n')
# sm_counts = collections.Counter()
# with open('sportsmole commentary comment count.json', 'r', encoding='utf8') as filecontents:
#     raw_count = json.load(filecontents)
# for count in raw_count:
#     sm_counts[count] = raw_count[count]
# g_counts = collections.Counter()
# with open('goal_com commentary comment count.json', 'r', encoding='utf8') as filecontents:
#     raw_count = json.load(filecontents)
# for count in raw_count:
#     g_counts[count] = raw_count[count]
# max_count = max([int(x) for x in sm_counts.keys()] + [int(x) for x in g_counts.keys()])
# sm_max_val = sum(sm_counts.values())
# g_max_val = sum(g_counts.values())
# print(np.average([x for x in range(max_count)], weights=[g_counts[str(x)] / sm_max_val for x in range(max_count)]))
# with open('comment_counts.csv', 'w+', encoding='utf8') as filecontents:
#     filecontents.write('count, sportsmole, goal\n')
#     for count in range(max_count):
#         filecontents.write(str(count) + ', ' + str(sm_counts[str(count)]/sm_max_val) + ', ' + str(g_counts[str(count)] / g_max_val) + '\n')

# with open('provider comparison.json', 'r', encoding = 'utf8') as filecontents:
#     data = json.load(filecontents)
#
# # with open('human machine comparison.json', 'r', encoding='utf8') as filecontents:
# #   data = json.load(filecontents)
#
# sportsmole_data = data['sportsmole']
# goal_data = data['goal']
#
# sportsmole_data = sportsmole_data.values()
# goal_data = goal_data.values()
#
# plt.hist(sportsmole_data, bins = np.geomspace(0, 6, 100), label = 'sportsmole, ' + str(sum(sportsmole_data)) + ' words')
# plt.hist(goal_data, bins = np.logspace(0, 6, 100), label = 'goal.com, ' + str(sum(goal_data)) + ' words')
# plt.yscale('log')
# plt.gca().set_xscale('log')
# plt.legend(loc = 'upper right')
# plt.title('Word frequency of football commentary')
# plt.ylabel('Word frequency')
# plt.xlabel('Number of words')
# plt.show()
