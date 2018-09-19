import newspaper as nws
import bs4 as bs
from datetime import date, datetime, timedelta
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common import action_chains
from selenium.common.exceptions import TimeoutException as TimeoutError_
from selenium.common.exceptions import MoveTargetOutOfBoundsException as OutOfBoundsError
import re
import json
from random import randint

configuration = nws.Config()
configuration.fetch_images = False
configuration.follow_meta_refresh = True

league_list = ["Europa League", "FA Cup", "Championship", "Champions League", "EFL Cup", "Premier League", "La Liga", "League One", "League Two",
               "Bundesliga", "Serie A", "Ligue 1"]


def datespan(start_date, end_date, delta):
    """generates daily time stamps of the format yyyy-mm-dd.

    Takes: start and end date and a time step.
    Returns: an iterable date."""
    current_date = start_date
    while current_date < end_date:
        yield current_date
        current_date += delta




def link_transformation(link):
    """chooses the right sub-page for goal.com match commentary.

    Takes: a list to matches from goal.com.
    Returns: the same list with /commentary-result/ added at the proper place."""
    transformed_link = []
    breakup = link.split('/')
    breakup.insert(-1, 'commentary-result')
    link = '/'.join(breakup)
    return link


def url_generator_sportmole(start_page, end_page):
    """creates a list of links to individual overview pages for sportsmole.co.uk.

    Takes: start- and endpage.
    Returns a list of pages."""
    list = []
    for i in range(end_page - start_page):
        list.append('https://www.sportsmole.co.uk/football/live-commentary/page-' + str(start_page + i))
    return list


def match_link_sportsmole(url_list):
    """builds a list of matches based on correct link pages on sportsmole.co.uk.

    Takes: A list of webpages.
    Returns: A list of links to individual commentary pages."""
    first = "list_rep list_odd list_rep_first"
    even = "list_rep list_even"
    odd = "list_rep list_odd"
    overall_list = []
    for page in url_list:
        overview = nws.build(page)
        overview.download()
        overview_soup = bs.BeautifulSoup(overview.html, 'lxml')
        content_soup = overview_soup.find_all('a', class_=[first, even, odd])
        for child in content_soup:
            overall_list.append('https://www.sportsmole.co.uk' + child.get('href'))
    return overall_list


def commentary_extraction_sportsmole(link):
    """Collects the comments off a single sportsmole commentary website

    Takes: A valid link to a sportsmole sports commentary website
    Returns: Dictionary with the keys:  sportsmole link
                                                       home team
                                                       away team
                                                       home score
                                                       away score
                                                       match date
                                                       league title
                                                       commentary sportsmole"""
    print(link)  # for debug purposes
    match_dict = {}
    match_dict['sportsmole link'] = str(link)
    match_comment = nws.build(link)
    match_comment.download()
    match_soup = bs.BeautifulSoup(match_comment.html, 'lxml')
    team_and_score = match_soup.find(id='content').find(class_='game_header').find(class_='game_header_top')
    try:
        home_team = team_and_score.find(class_ = 'game_header_bar_teams').find(class_ = 'game_header_bar_team left').find('span', class_ = 'desktop_only').string
    except AttributeError:
        home_team = team_and_score.find(class_ = 'game_header_bar_teams').find(class_ = 'game_header_bar_team left').string
    try:
        away_team = team_and_score.find(class_ = 'game_header_bar_teams').find(class_ = 'game_header_bar_team left').next_sibling.next_sibling.find('span', class_ = 'desktop_only').string
    except AttributeError:
        away_team = team_and_score.find(class_ = 'game_header_bar_teams').find(class_ = 'game_header_bar_team').string
    score = team_and_score.find(class_='game_header_score').string
    home_score, away_score = score.split('-')
    match_dict['home team'] = str(home_team)
    match_dict['away team'] = str(away_team)
    match_dict["home score"] = str(home_score)
    match_dict["away score"] = str(away_score)
    match_content = match_soup.body.find(id="article_body")
    find_date = team_and_score.find(class_ = 'game_header_bar_date').find('span').string
    try:
        match_date = datetime.strptime(find_date, '%b %d, %Y at %I.%M%p UK').date()
    except ValueError:
        match_date = datetime.strptime(find_date, '%b %d, %Y at %I%p UK').date()
    match_dict["match date"] = str(match_date)
    breadcrumps = match_soup.find(id="breadcrumb").find_all(class_=re.compile("bc_item bc_[0-9]"))
    league = None
    for breadcrump_text in reversed(breadcrumps):
        if not breadcrump_text.find('span', attrs={"itemprop": "title"}) is None:
            if breadcrump_text.find('span', attrs={"itemprop": "title"}).string in league_list:
                league = breadcrump_text.find('span', attrs={"itemprop": "title"}).string
    if not league == None:
        match_dict["league title"] = str(league)
    else:
        print("Warning: league not found in instance: " + link)

    # comment collection
    comments = []
    if not match_content.find(class_='livecomm') is None:
        for child in match_content.find_all(class_='livecomm'):
            time_stamp = child.find(class_='period')
            if 'min' in time_stamp.string:
                comment_string = "".join(time_stamp.next_sibling.stripped_strings)
                comments.append([str(time_stamp.string), str(comment_string)])
    else:
        for child in match_content.find_all('p'):
            if not child.strong is None and not child.strong.next_sibling is None:
                comments.append([str(child.strong.string), str(child.strong.next_sibling.string)])
    match_dict["commentary sportsmole"] = comments
    return match_dict


def link_generator_talksport(links):
    talksport_match_links = []
    for link in links:  # One for each league
        match_links = nws.build(links[link])
        match_links.download()
        link_soup = bs.BeautifulSoup(match_links.html, 'lxml')
        link_list = []
        for child in link_soup.find_all(class_='matches'):
            individual_link = child.find(class_='match-link').find('a').get('href')
            link_list.append(individual_link)
        link_dict = {link: link_list}  # format: League: [list of matches]
        talksport_match_links.append(link_list)
    return talksport_match_links  # format: [list of {League: [list of matches]}]


links_talksport = {'Premier': 'https://talksport.com/football/premier-league/results'}


def commentary_extraction_talksport(link):
    match_dict = {}
    comments = []
    driver = webdriver.Firefox()
    driver.get(link)
    try:
        element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'tab-commentary')))
        WebDriverWait(driver, 1)
        commentary_code = element.get_attribute('outerHTML')
        match_soup = bs.BeautifulSoup(commentary_code, 'lxml')
    finally:
        driver.quit()
    ##match info
    match_info_soup = match_soup.find(class_='pane-content').find(class_='Opta Opta-Normal')
    match_dict['home team'] = match_info_soup.find(class_=re.compile('^Opta-Team Opta-Home Opta-Team-Left Opta-TeamName Opta-Team')).string
    match_dict['away team'] = match_info_soup.find(class_=re.compile('^Opta-Team Opta-Away Opta-Team-Right Opta-TeamName Opta-Team')).string
    match_dict['home score'] = match_info_soup.find(class_=re.compile('^Opta-Score Opta-Home')).string
    match_dict['away score'] = match_info_soup.find(class_=re.compile('^Opta-Score Opta-Away')).string
    match_dict['league title'] = match_info_soup.find(class_='Opta-MatchHeader-Details').find(class_='Opta-Competition Opta-Comp-8').string
    match_date = match_info_soup.soup.find(class_='Opta-Date').string
    match_dict['match date'] = datetime.strptime(match_date, '%A %d %B %Y')
    for child in match_soup.find_all('li'):
        time_string = ''
        for string in child.find(class_='Opta-Time').strings:
            time_string += string
        time_string = time_string.replace(u'\xa0', ' ')
        comments.append([time_string, child.find(class_='Opta-comment').string])
        print([time_string, child.find(class_='Opta-comment').string])
    match_dict['commentary talksport'] = comments
    return match_dict


def url_generator_goal(start_date, end_date, delta=timedelta(days=1)):
    """generates a valid url for goal.com daily overviews.

    Takes: start and end date of the period in question and a possible time step.
    Returns: a list of urls. and the respective days."""
    url = []
    for day in datespan(start_date, end_date, delta):
        url.append("http://www.goal.com/en/results/" + str(day))
    return url


def match_link_goal_com(url_list):
    """extracts links to matches from an overview website.

    Takes: a list of urls valid for goal.com match overview website.
    Returns: a list of links to all matches in the period of the url list"""
    overall_list = []
    for link in url_list:
        overview = nws.build(link)
        overview.download()
        overview_soup = bs.BeautifulSoup(overview.html, 'lxml')
        for child in overview_soup.body.find_all('a', attrs= {'class':"match-main-data-link"}):
            page_link = child.get('href')
            overall_list.append(link_transformation(page_link))
    return overall_list # flat list of links to matches


def commentary_extraction_goal_com(link):
    """Extracts football commentary from the goal.com individual matches website.

    Takes: a list of links to individual match websites, with the first entry containing the match day.
    Returns: time stamps and corresponding comments in a list, grouped in a list."""
    print(link)
    match_dict = {}
    match_dict['goal.com link'] = link
    driver = webdriver.Firefox()
    driver.set_page_load_timeout(20)
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'content')))
        WebDriverWait(driver, 0.5)
        match_comment = driver.page_source
    except TimeoutError_:
        match_comment = driver.page_source
    finally:
        driver.close()
    match_soup = bs.BeautifulSoup(match_comment, 'lxml')
    comments_section = match_soup.find(class_ = 'mr-gutters main-container clearfix').find(class_ = 'container-match').find(class_ = 'widget-match-commentary clearfix').find_all(class_ = 'comment')
    comments = []
    for child in comments_section:
        try:
            comments.append([str(child.find(class_ = 'time').string), str(child.find(class_ = 'text').string)])
        except AttributeError:
            pass
    match_dict["commentary goal.com"] = comments
    information = match_soup.find(class_="mr-gutters")
    match_date = information.find(class_ = 'widget-match-header widget-match-header--pld widget-match-header--post').meta['content']
    home_team = information.find('a', attrs={'itemprop': "homeTeam"}).find(class_="widget-match-header__name--full").string
    away_team = information.find('a', attrs={'itemprop': "awayTeam"}).find(class_="widget-match-header__name--full").string
    score = information.find(class_="widget-match-header__score").find('span', attrs={'data-slot': 'score'}).string
    league = match_soup.find('div', attrs= {'class': 'widget-match-recirculation', 'data-module': 'match/recirculation'}).find(class_ = 'widget-headline').string
    home_score, away_score = score.split(" - ")
    match_dict["home team"] = str(home_team)
    match_dict["away team"] = str(away_team)
    match_date = datetime.strptime(match_date, '%Y-%m-%dT%H:%M:%S+00:00').date()
    match_dict["match_date"] = str(match_date)
    match_dict["home score"] = str(home_score)
    match_dict["away score"] = str(away_score)
    match_dict["league title"] = str(league)
    return match_dict


def link_generator_onefootball(link_dict):
    match_link_dict = {}
    for link in link_dict:
        id_counter = 0
        try:
            driver = webdriver.Firefox()
            driver.get(link_dict[link])
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'mb-xxl')))
            WebDriverWait(driver, 0.5)
            page_sources = []
            for counter in range(0, 40):
                left_arrow = driver.find_element_by_xpath('/html/body/of-app/main/of-competition-nav/div/div/of-competition-tab-matches/div/section/of-competition-matches/div[1]/nav/span[1]')
                clicking = action_chains.ActionChains(driver).move_to_element(left_arrow).click(left_arrow)
                clicking.perform()
                WebDriverWait(driver, 15) #wait for page loading
                page_sources.append(driver.page_source)
        finally:
            driver.close()
        page_sources = list(set(page_sources)) # remove duplicates
        for counter, page_source in enumerate(page_sources):
            page_soup = bs.BeautifulSoup(page_source, 'lxml')
            match_links = []
            for match_link in page_soup.find_all(class_="match-cards LARGE"):
                for actual_link in match_link.find_all('a'):
                    match_links.append(actual_link.get('href'))
            match_link_dict[link + ' ' + str(counter)] = match_links
    return match_link_dict  ##flat dictionary, entries: <League> [0-9]+


def commentary_extraction_onefootball(link):
    print(link)
    scroll_wait = 1.5
    match_dict = {}
    try:
        driver = webdriver.Firefox()
        driver.get(link)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "of-match-live-experience")))
        load_more = driver.find_element_by_xpath('/html/body/div[6]/div/div/div/div/div/div[1]/div/section/div[8]/article/of-pager/div/div/div/button')
        driver.execute_script('window.scrollTo(0,arguments[0]);', load_more.location['y']-100)
        WebDriverWait(driver, 1).until(EC.visibility_of(load_more))
        load_more_position = load_more.location['y']
        scroll_position = 100
        while scroll_position < load_more_position - 150:
            driver.execute_script('window.scrollTo(0,arguments[0]);', scroll_position)
            WebDriverWait(driver, 0.5)
            scroll_position += 30 + randint(-10, 10)
        driver.execute_script('window.scrollTo(0,arguments[0]);', load_more_position - 150)
        load_more = driver.find_element_by_xpath('/html/body/div[6]/div/div/div/div/div/div[1]/div/section/div[8]/article/of-pager/div/div/div/button')
        WebDriverWait(driver, 1)
        load_more_click = action_chains.ActionChains(driver).move_to_element(load_more).click(load_more)
        load_more_click.perform()
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, scroll_wait)
        last_height = driver.execute_script("return window.pageYOffset")
        while True:
            driver.execute_script("window.scrollTo(0, arguments[0]);", scroll_position)
            WebDriverWait(driver, scroll_wait)
            new_height = driver.execute_script("return window.pageYOffset")
            scroll_position += 100
            if new_height == last_height:
                break
            last_height = new_height
        hand_over = driver.page_source
    finally:
        driver.close()
    page_soup = bs.BeautifulSoup(hand_over, 'lxml')
    comment_soup = page_soup.find_all('li')
    match_date = comment_soup[0].find('time').get('datetime')
    commentary = []
    for child in comment_soup:
        timestamp = child.find(class_='time text-center').string
        comment = child.find(class_='action-description').string
        commentary.append([str(timestamp), str(comment)])
    match_dict["commentary onefootball"] = commentary
    match_info_soup = page_soup.find(class_="content-header-body").find(class_="of-row pt-lg pb-none")
    home_team = match_info_soup.find(class_="team team-home").get('title')
    away_team = match_info_soup.find(class_="team team-away").get('title')
    score = match_info_soup.find(class_="game-result mt-sm mb-sm text-center").string
    home_score, away_score = score.split(' : ')
    match_dict["home team"] = str(home_team)
    match_dict["away team"] = str(away_team)
    match_dict["home score"] = str(home_score)
    match_dict["away score"] = str(away_score)
    #match_date = page_soup.find('div', attrs = {'ng-if': '::vm.displayDate'}).find(class_="m-none game-info-small-box").string
    match_dict["match date"] = str(datetime.strptime(match_date, '%Y-%m-%dT%H:%M:%SZ').date())
    return match_dict


# test_dict = {'test': "https://webapp.onefootball.com/match/9/541716?locale=en"}
# test = commentary_extraction_onefootball(test_dict['test'])
# print(test['commentary onefootball'][:10])
# print(test['commentary onefootball'][-10:])
# print(test['away team'])
# print(test['match date'])



def persistent(website, current_counter, filename = 'persistent.json'):
    with open(filename, 'r') as filecontents:
        stored_data = json.load(filecontents)
    stored_data[website] = current_counter
    with open(filename, 'w') as filecontents:
        json.dump(stored_data, filecontents)


