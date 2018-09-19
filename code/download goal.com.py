import json
import datagrabber


# from datetime import date
# start_date = date(year=2017, month=1, day=1)
# end_date = date(year=2018, month=4, day=16)
#
# goal_urls = datagrabber.url_generator_goal(start_date, end_date)
# goal_links = datagrabber.match_link_goal_com(goal_urls)
# with open('goal_com links.json', 'w+') as filecontents:
#     link_dict = {}
#     for counter, link in enumerate(goal_links):
#         link_dict['link ' + str(counter)] = link
#     json.dump(link_dict, filecontents)

with open('goal_com links.json', 'r') as filecontents:
    goal_links = json.load(filecontents)


with open('persistent.json', 'r') as persistent:
    start = json.load(persistent)['goal'] + 1

# start = 6361
filename = 'goal_com commentary.json'
end = len(goal_links)
# start = 1083

#
for counter in range(start, end):
    with open(filename, 'r', encoding='utf8') as filecontents:
        dictionary_list = json.load(filecontents)
    print(str(counter))
    link = goal_links['link ' + str(counter)]
    try:
        dictionary_data = datagrabber.commentary_extraction_goal_com(link)
        dictionary_list['match nr ' + str(counter)] = dictionary_data
        with open(filename, 'w', encoding='utf8') as filecontents:
            json.dump(dictionary_list, filecontents, ensure_ascii=False)
    except AttributeError:
        print('Error in: ' + link)
        pass
    datagrabber.persistent('goal', counter)