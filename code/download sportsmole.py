import json
import datagrabber

# sportsmole_urls = datagrabber.url_generator_sportmole(1, 137)
# sportsmole_links = datagrabber.match_link_sportsmole(sportsmole_urls)
# with open('sportsmole links.json', 'w+') as filecontents:
#     link_dict = {}
#     for counter, link in enumerate(sportsmole_links):
#         link_dict['link ' + str(counter)] = link
#     json.dump(link_dict, filecontents)

with open('sportsmole links.json', 'r') as filecontents:
    sportsmole_links = json.load(filecontents)

with open('persistent.json', 'r') as persistent:
    start = json.load(persistent)['sportsmole'] + 1


filename = 'sportsmole commentary.json'
end = len(sportsmole_links)
# start = 2819

# with open('sportsmole commentary.json', 'w+', encoding='utf8') as filecontents:
#     dictionary_list = []
#     match_dict = datagrabber.commentary_extraction_sportsmole(sportsmole_links[0])
#     dictionary_list.append(match_dict)
#     json.dump(dictionary_list, filecontents, ensure_ascii=False)

for counter in range(start, end):
    with open('sportsmole commentary.json', 'r', encoding='utf8') as filecontents:
        dictionary_list = json.load(filecontents)
    print(str(counter))
    link = sportsmole_links['link ' + str(counter)]
    try:
        dictionary_data = datagrabber.commentary_extraction_sportsmole(link)
        dictionary_list['match nr ' + str(counter)] = dictionary_data
        with open('sportsmole commentary.json', 'w', encoding='utf8') as filecontents:
            json.dump(dictionary_list, filecontents, ensure_ascii=False)
    except AttributeError:
        continue
    datagrabber.persistent('sportsmole', counter)