import nltk
import json
import re
import collections
import numpy as np
from scipy.stats import norm, poisson

try:
    raise FileNotFoundError
    with open('players organised.json', 'r', encoding='utf8') as filecontents:
        database = json.load(filecontents)
    players = database['players']
    teams = database['teams']
    nationalities = database['nationality']
except FileNotFoundError:
    with open('all players PL.txt', 'r', encoding='utf8') as filecontents:
        raw = filecontents.read()

    lines = raw.split('\n')
    players = {}
    teams = {}
    nationalities = {}
    for counter, line in enumerate(lines):
        if re.match('[0-9]+\.\t', line):
            _, name, team, _ = line.lower().split('\t')
            nationality = lines[counter + 1].lower()
            for part_names in name.split(' '):
                if part_names not in players and part_names not in ['can', 'will', 'field', 'hazard', 'long', 'nathan', 'jack', 'richarlison', 'zanka', 'césar', 'kevin', 'de', 'abdoulaye', 'shane', 'pablo', 'joe', 'ashley', 'matt', 'bernardo', 'wilfried']:
                    players[part_names] = {'nationality': nationality, 'team': team, 'tags': []}
            for part_teams in team.split(' '):
                if team not in teams and team not in ['and']:
                    teams[team] = {'tags': []}
            if nationality not in nationalities:
                nationalities[nationality] = {'tags': None}
    # teams = list(set(teams))

    with open('players organised.json', 'w+', encoding='utf8') as filecontents:
        json.dump({'players': players, 'teams': teams, 'nationality': nationalities}, filecontents)

try:
    raise FileNotFoundError
    with open('teams tags.json', 'r', encoding='utf8') as filecontents:
        teams = json.load(filecontents)
    with open('nationality tagbase.json', 'r', encoding='utf8') as filecontents:
        tag_database = json.load(filecontents)
    with open('players tags.json', 'r', encoding='utf8') as filecontents:
        players = json.load(filecontents)
except FileNotFoundError:
    with open('sportsmole commentary.json', 'r', encoding='utf8') as filecontents:
        commentary = json.load(filecontents)
    examine = True
    for match in commentary:
        try:
            if commentary[match]['league title'] == 'Premier League':
                for time_stamp, comment in commentary[match]['commentary sportsmole']:
                    player = None
                    team = None
                    tagged_sentence = nltk.pos_tag(nltk.tokenize.word_tokenize(comment))
                    if examine:
                        print(tagged_sentence)
                        examine = False
                    for word, tag in tagged_sentence:
                        if word.lower() in players and player is None:
                            player = [word.lower()]
                        elif word.lower() in players:
                            player.append(word.lower())
                        if word.lower() in teams and team is None:
                            team = [word.lower()]
                        elif word.lower() in teams:
                            team.append(word.lower())
                    if player is not None:
                        for word, tag in tagged_sentence:
                            if tag == 'JJ' or tag == 'RB':
                                for individual in player:
                                    players[individual]['tags'].append(word.lower())
                    if team is not None:
                        for word, tag in tagged_sentence:
                            if tag == 'JJ' or tag == 'RB':
                                for individual in team:
                                    teams[individual]['tags'].append(word.lower())
        except KeyError:
            continue

    for player in players:
        word_count = collections.Counter()
        for word in players[player]['tags']:
            word_count[word] += 1
        if nationalities[players[player]['nationality']]['tags'] is None:
            nationalities[players[player]['nationality']]['tags'] = word_count
        else:
            for word in word_count:
                nationalities [players[player]['nationality']]['tags'][word] += word_count[word]
        players[player]['tags'] = word_count
    for team in teams:
        word_count = collections.Counter()
        for word in teams[team]['tags']:
            word_count[word] += 1
        teams[team]['tags'] = word_count

    tag_database = {nationality: nationalities[nationality]['tags'].most_common() for nationality in nationalities}

    with open('nationality tagbase.json', 'w+', encoding='utf8') as filecontents:
        json.dump(tag_database, filecontents)
    with open('players tags.json', 'w+', encoding='utf8') as filecontents:
        json.dump(players, filecontents)
    with open('teams tags.json', 'w+', encoding='utf8') as filecontents:
        json.dump(teams, filecontents)

# tag_database # {country: [(tag, number)]
full_tag_set_players = collections.Counter()
for player in players:
    for tag in players[player]['tags']:
        full_tag_set_players[tag] += players[player]['tags'][tag]

full_tag_set_teams = collections.Counter()
for team in teams:
    for tag in teams[team]['tags']:
        full_tag_set_teams[tag] += teams[team]['tags'][tag]

def p_value(n, p, value):
    mu = n * p
    sigma = np.sqrt(n * p * (1 - p))
    z = (value - mu) / sigma
    return norm.cdf(z)

# interesting = 'white, dangerous, steal, stealy, aggressive, hazard, bad, black'.split(', ')
interesting = 'poor, dangerous, aggressive, fantastic, bad, amazing, great, angry, frustrated'.split(', ')

print('PLAYERS')
print(len(players))
for individual in players:
    for tag in players[individual]['tags']:
        n = sum(players[individual]['tags'].values())
        p = players[individual]['tags'][tag] / full_tag_set_players[tag]
        k = players[individual]['tags'][tag]
        p_v = p_value(n, p, k)
        if p_v < 0.05 and k > 10 and tag in interesting:
            print(individual + ' (' + str(n) + ') & ' + tag + ' (' + str(k) + ') & ' + str(n * p)+ ' & $' + str(p_v) + '$\\\\')

print('\n\n\n\n TEAMS')

for team in teams:
    for tag in teams[team]['tags']:
        n = sum(teams[team]['tags'].values())
        p = teams[team]['tags'][tag] / full_tag_set_teams[tag]
        k = teams[team]['tags'][tag]
        p_v = p_value(n, p, k)
        if p_v < 0.05 and k > 10 and tag in interesting:
            print(team + ' (' + str(n) + ' tags in total), ' + tag + ' (' + str(k) + '), probability: ' + str(p)  + ', expected (np): ' + str(n * p)+ ', p value: ' + str(p_v))

print('\n\n\n\n NATIONALITIES')

for nation in nationalities:
    for tag in nationalities[nation]['tags']:
        n = sum(nationalities[nation]['tags'].values())
        p = nationalities[nation]['tags'][tag] / full_tag_set_players[tag]
        k = nationalities[nation]['tags'][tag]
        p_v = p_value(n, p, k)
        if p_v < 0.05 and k > 10 and tag in interesting:
            print(nation + ' (' + str(n) + ') & ' + tag + ' (' + str(k) + ') & ' + str(n * p) + ' & $' + str(p_v) + '$\\\\')