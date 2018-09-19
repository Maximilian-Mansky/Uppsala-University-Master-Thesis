import nltk
import json
import matplotlib.pyplot as plt
import os
from string import punctuation
import collections

sportsmole_green = (69/255, 125/255, 20/255)
goal_blue = (0, 100/255, 163/255)
goal2 = (20/255, 50/255, 103/255)

stopwords = punctuation
# absolute_count_premier = absolute_count_champions = absolute_count_ligue = 0


def load_raw_data(filename, commentary_name, league = None):
    """loads the raw data from a collected commentary file (json structure)

    Takes:  the filename (string)
                the commentary key (one of the following: 'sportsmole commentary', 'goal_com commentary', 'commentary onefootball')
                optionally a league title, so that only data of a particular team is loaded
    Returns: A list of commentary elements (excluding timestamps)"""
    data = []
    with open(filename, 'r', encoding='utf8') as filecontents:
        dictionary = json.load(filecontents)
    if league is None:
        for key in dictionary:
            for list_element in dictionary[key][commentary_name]:
                data.append(list_element[1])
    else:
        for key in dictionary:
            try:
                if dictionary[key]['league title'] == league:
                    for list_element in dictionary[key][commentary_name]:
                        data.append(list_element[1])
            except KeyError:
                continue
    return data


def data_carryover(data, league, stopwords = []):
    fdist = nltk.probability.FreqDist()
    for word in data[league]:
        if not word in stopwords:
            fdist[word] = data[league][word]
    return fdist

sm_data = load_raw_data('sportsmole commentary.json', 'commentary sportsmole')
g_data_human = load_raw_data('goal_com commentary.json', 'commentary goal.com', 'Premier League')
g_data_machine = load_raw_data('goal_com commentary.json', 'commentary goal.com', 'Bundesliga') +\
                 load_raw_data('goal_com commentary.json', 'commentary goal.com', 'Ligue 1')
sm_word_count = collections.Counter()
gh_word_count = collections.Counter()
gm_word_count = collections.Counter()

for comment in sm_data:
    for word in nltk.tokenize.word_tokenize(comment.lower()):
        sm_word_count[word] += 1
for comment in g_data_human:
    for word in nltk.tokenize.word_tokenize(comment.lower()):
        gh_word_count[word] += 1
for comment in g_data_machine:
    for word in nltk.tokenize.word_tokenize(comment.lower()):
        gm_word_count[word] += 1


# data_premier = load_raw_data('goal_com commentary.json', 'commentary goal.com', 'Premier League')
# data_bundesliga = load_raw_data('goal_com commentary.json', 'commentary goal.com', 'Bundesliga')
# data_ligue_1 = load_raw_data('goal_com commentary.json', ' commentary goal.com', 'Ligue 1')
# data_premier = ''.join(data_premier)
# data_machine = ''.join(data_bundesliga + data_ligue_1)
#
# fdist_premier = nltk.probability.FreqDist()
# fdist_machine = nltk.probability.FreqDist()
# abs_count_premier = abs_count_machine = 0
#
#
# for word in nltk.tokenize.word_tokenize(data_premier):
#     fdist_premier[word.lower()] += 1
#     abs_count_premier += 1
#
# for word in nltk.tokenize.word_tokenize(data_machine):
#     fdist_machine[word.lower()] += 1
#     abs_count_machine += 1
#
# print('human:' + str(len(fdist_premier)) + ', ' + str(abs_count_premier) + ' words')
# print('human:' + str(len(fdist_machine)) + ', ' + str(abs_count_machine) + ' words')
#
# with open('human machine comparison.json', 'w+', encoding='utf8') as filecontents:
#     json.dump({'human': fdist_premier, 'machine': fdist_machine}, filecontents)
#
# with open('human machine comparison.json', 'r', encoding='utf8') as filecontents:
#     data = json.load(filecontents)


# data_goal = load_raw_data('goal_com commentary.json', 'commentary goal.com')
# data_sportsmole = load_raw_data('sportsmole commentary.json', 'commentary sportsmole')
#
# data_goal = ''.join(data_goal)
# data_sportsmole = ''.join(data_sportsmole)

# fdist_goal = nltk.probability.FreqDist()
# fdist_sportsmole = nltk.probability.FreqDist()

# absolute_count_goal = absolute_count_sportsmole = 0

# for word in nltk.tokenize.word_tokenize(data_goal):
#     fdist_goal[word.lower()] += 1
#     absolute_count_goal += 1
# for word in nltk.tokenize.word_tokenize(data_sportsmole):
#     fdist_sportsmole[word.lower()] += 1
#     absolute_count_sportsmole += 1

# with open('provider comparison.json', 'w+', encoding = 'utf8') as filecontents:
#     json.dump({'goal': fdist_goal, 'sportsmole': fdist_sportsmole}, filecontents)


# with open('provider comparison.json', 'r', encoding = 'utf8') as filecontents:
#     data = json.load(filecontents)

# fdist_machine = data_carryover(data, 'machine', stopwords)
# absolute_count_machine = sum(data['machine'].values())
# fdist_human = data_carryover(data, 'human', stopwords)
# absolute_count_human = sum(data['human'].values())

print('Number of unique words: ', len(sm_word_count), ' in sportsmole, ', len(gh_word_count), ' in goal.com human commentary')
# print('word with highest occurence (excluding stopwords);', highest_occurrence)
print('Total number of words:', sum(sm_word_count.values()), ' in sportsmole commentary, ', sum(gh_word_count.values()), ' in goal.com human commentary')

samples = [item for item, _ in sm_word_count.most_common(100)]
sm_freqs = [sm_word_count[sample] / sum(sm_word_count.values()) for sample in samples]
gh_freqs = [gh_word_count[sample] / sum(gh_word_count.values()) for sample in samples]
gm_freqs = [gm_word_count[sample] / sum(gm_word_count.values()) for sample in samples]

plt.plot(sm_freqs, label ='sportsmole', color=sportsmole_green)
plt.plot(gh_freqs, label ='goal.com human', color=goal_blue)
plt.plot(gm_freqs, label='goal.com machine', color=goal2)
#
plt.legend(loc = 'upper right')
plt.title('Word frequency analysis')
plt.yscale('log')
plt.xticks(range(len(samples)), samples, rotation = 90)

plt.show()
#
# os.system('say "The code has finished"')
