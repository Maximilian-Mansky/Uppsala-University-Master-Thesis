import json
import datagrabber

# link_dict_onefootball = { "Premier League": "https://www.onefootball.com/en/competition/premier-league-9/matches",
#                                     "Europa League": "https://www.onefootball.com/en/competition/europa-league-7/matches",
#                                     "Champions League": "https://www.onefootball.com/en/competition/champions-league-5/matches",
#                                     "Primera Division": "https://www.onefootball.com/en/competition/primera-division-10/matches",
#                                     "Bundesliga": "https://www.onefootball.com/en/competition/bundesliga-1/matches",
#                                     "Serie A": "https://www.onefootball.com/en/competition/serie-a-13/matches"}
# matchlinks_new = datagrabber.link_generator_onefootball(link_dict_onefootball)
#
# with open('onefootball links.json', 'r', encoding='utf8') as filecontents:
#     matchlinks_old = json.load(filecontents)
#
# matchlinks_onefootball = {**matchlinks_old, **matchlinks_new}
#
# with open('onefootball links.json', 'w', encoding='utf8') as filecontents:
#     json.dump(matchlinks_onefootball, filecontents)
filename = 'onefootball commentary.json'

with open('onefootball links.json', 'r') as filecontents:
    league_dictionary = json.load(filecontents)


with open('persistent.json', 'r', encoding = 'utf8') as persistent:
    persistency= json.load(persistent)
    match_day = persistency['onefootball']
    advance = persistency['onefootball match']
    link_start = persistency['onefootball link counter'] + 3


for counter in range(match_day, 35):
    with open(filename, 'r', encoding='utf8') as filecontents:
        dictionary_list = json.load(filecontents)
    print(str(counter))
    for link_counter in range(link_start, 10):
        print('   ', link_counter)
        link = league_dictionary['Premier League ' + str(counter)][link_counter]
        dictionary_data = datagrabber.commentary_extraction_onefootball(link)
        dictionary_list['Premier League ' + str(advance)] = dictionary_data
        advance += 1
        if link_counter == 9:
            link_start = 0
        with open(filename, 'w', encoding='utf8') as filecontents:
            json.dump(dictionary_list, filecontents, ensure_ascii=False)
        datagrabber.persistent('onefootball', counter)
        datagrabber.persistent('onefootball match', advance)
        datagrabber.persistent('onefootball link counter', link_counter)

