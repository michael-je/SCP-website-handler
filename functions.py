
from bs4 import BeautifulSoup
import requests
from webbrowser import open as wp_open
from time import sleep
from random import choice

from classes import SCP
from constants import headers, homepage_URL
import db
import global_vars


def debug_display_requests_count():
    # prints out how many times the code has sent a request to the wiki since it started running
    # counters are stored in global_vars
    print(f'{global_vars.debug_requests_count - global_vars.debug_requests_count_last} requests sent.')
    print(f'{global_vars.debug_requests_count} requests sent in total.')
    global_vars.debug_requests_count_last = global_vars.debug_requests_count


def reformat_SCP_num(scp_number):
    # reformats an integer value scp_number to a string, since integers can not have leading 0s
    # this is necessary to construct some of the URLs
    str_number = str(scp_number)
    while (len(str_number)) < 3:
        str_number = '0' + str_number
    return str_number


def get_scp_series_links():
    # The SCP wiki divides the SCPs to different pages in groupings of 1000, this functions scrapes the
    # homepage of the wiki to find the links to each page
    main_source = requests.get(homepage_URL, headers=headers)               # request
    global_vars.debug_requests_count += 1
    main_soup = BeautifulSoup(main_source.text, 'lxml')
    scp_series_menu = main_soup.find_all('div', class_='menu-item')[2]
    scp_series_anchors = scp_series_menu.find_all('a')

    scp_series_links = []
    for i in scp_series_anchors:
        path_link = str(i).split('"')[1]
        full_link = homepage_URL + path_link[1:]
        scp_series_links.append(full_link)

    return scp_series_links


def update_scp(scp_number, arg_scp_name=None):
    # This functions scrapes the wiki to find all desired data about the SCP under the given scp_number.
    # It does this piece by piece and then adds all the data to the database if the SCP exists
    str_number = reformat_SCP_num(scp_number)
    scp_link = f'http://www.scp-wiki.net/scp-{scp_number}'
    source = requests.get(scp_link, headers=headers)                        # request
    global_vars.debug_requests_count += 1
    soup = BeautifulSoup(source.text, 'lxml')

    # check whether SCP page exists
    try:
        exists_check = soup.find('h1', id='toc0').text
        if exists_check == "This page doesn't exist yet!":
            print("SCP doesn't exist yet!")
            # Even if the SCP doesn't exist we add it to the database as non-existent.
            # This allows us to fill the database with info on all scps later.
            new_scp = SCP(scp_number, "N/A", "N/A", "N/A", "N/A", 0, exists=0)
            result = db.add_scp(new_scp)
            if result == -1:
                db.update_scp(new_scp)
            return
    except AttributeError:
        pass

    # Gets the name of the SCP if not supplied via argument
    # (only accessible via the SCP series links otherwise)
    if arg_scp_name:
        name = arg_scp_name
    else:
        if len(str_number) < 4:
            series_link = get_scp_series_links()[0]
        else:
            series_link = get_scp_series_links()[int(str_number[0])]
        scp_list_index = int(str_number[-2:])
        main_list_index = int(str_number[-3])
        series_source = requests.get(series_link, headers=headers)          # request
        global_vars.debug_requests_count += 1
        series_soup = BeautifulSoup(series_source.text, 'lxml')
        scp_names_sublist = series_soup.find('div', class_='content-panel standalone series').select('ul')[main_list_index + 1].find_all('li')
        name = ' - '.join(scp_names_sublist[scp_list_index].text.split(" - ")[1:])

    page_content = soup.find('div', id='page-content')

    # find the SCP's rating
    try:
        rating = page_content.find('span', class_='number prw54353').text
        rating = ''.join([l for l in rating if l.isnumeric()])
    except AttributeError:
        # This value is stored as a string in the db
        rating = "Unknown"

    # checks whether the SCP has an image
    try:
        has_image = int(bool(page_content.find_all('div', recursive=False)[1].img))
    except IndexError:
        # has_image = False by deault as a catch-all
        has_image = 0

    # check whether the SCP has an unusual format (such as SCP 2000 and 2521)
    # SCPs with unusual format will be given "Unknown" as their object_class and False for has_image
    unusual_format = 0
    try:
        if has_image:
            if page_content.select('p')[1].text.split(' ')[0] != 'Item':
                unusual_format = 1
        else:
            if page_content.select('p')[0].text.split(' ')[0] != 'Item':
                unusual_format = 1
    except IndexError:
        unusual_format = 1

    # finds the SCP's object class. object_class = "Unknown" by default if it's format is unusual
    if not unusual_format:
        if has_image:
            object_class = page_content.find_all('p')[2].text
            object_class = ' '.join(object_class.split(' ')[2:])
        else:
            object_class = page_content.find_all('p')[1].text
            object_class = object_class.split(' ')[2]
    else:
        object_class = "Unknown"

    # construct an SCP object from the data
    new_scp = SCP(scp_number, name, object_class, rating, scp_link, has_image,
                  unusual_format=unusual_format)

    # tries to add the scp to the database and gets the result of whether it was successful
    result = db.add_scp(new_scp)
    if result == -1:
        # this block will run if the scp is already in the database
        # in this case we want to update it with the current data
        db.update_scp(new_scp)
        # 2 indicates that the scp was updated
        return 2
    # 1 indicates that the SCP was added
    return 1


def display_scp(scp_number, debug=False):
    # Finds data on an SCP from the database and displays it to the terminal
    # set debug=True for hidden data
    scp = db.get_scp(scp_number)
    if scp == -1:
        print(f"SCP-{scp_number} not in database!")
    else:
        scp.display(debug=debug)


def go_to_scp_page(scp_number):
    # opens the SCP webpage in a webbrowser
    URL = homepage_URL + 'scp-' + str(scp_number)
    wp_open(URL, new=2)


# create a function that returns a random SCP from the database
# use additional arguments to specify if it should include scps which are flagged with
# have_read, dont_want_to_read and/or exists. They are excluded by default.
def get_random_scp(not_read_yet=True, want_to_read=True, does_exist=True, is_favorite=False, read_later=False):
    extra_flags = []
    if not_read_yet:
        extra_flags.append("have_read")
    if want_to_read:
        extra_flags.append("dont_want_to_read")
    if does_exist:
        extra_flags.append("exists_online")
    if is_favorite:
        extra_flags.append("is_favorite")
    if read_later:
        extra_flags.append("read_later")
    candidates = db.get_available_scp_numbers(extra_flags)

    # here we filter through the candidate scps, continuing the loop (thus excluding the scp) if a condition is met
    filtered_candidates = []
    for scp in candidates:
        if scp.get("have_read") == 1:
            continue
        if scp.get("dont_want_to_read") == 1:
            continue
        if scp.get("exists_online") == 0:
            continue
        if scp.get("is_favorite") == 0:
            continue
        if scp.get("read_later") == 0:
            continue
        filtered_candidates.append(scp.get("number"))
    try:
        random_scp_number = choice(filtered_candidates)
    except IndexError:
        # -1 indicates that the search returned no results
        return -1
    return db.get_scp(random_scp_number)


def mark_scp_have_read_status(scp_number, have_read=True):
    # updates the desired scps have_read status as given by the second argument
    scp = db.get_scp(scp_number)
    if scp == -1:
        print("SCP not in database!")
        return -1
    scp.have_read = int(have_read)
    db.update_scp(scp)
    return 1


def mark_scp_dont_want_to_read_status(scp_number, dont_want_to_read=True):
    # updates the desired scps dont_want_to_read status as given by the second argument
    scp = db.get_scp(scp_number)
    if scp == -1:
        print("SCP not in database!")
        return -1
    scp.dont_want_to_read = int(dont_want_to_read)
    db.update_scp(scp)
    return 1


# todo refactor and fix this function to make it safe for use
def update_all_scps():                      # currently in debug, remove or edit list indexing to fix
    for link in [get_scp_series_links()[0]]:
        link_source = requests.get(link, headers=headers)                   # request
        global_vars.debug_requests_count += 1
        link_soup = BeautifulSoup(link_source.text, 'lxml')
        main_list = link_soup.find('div', class_='content-panel standalone series')
        main_list = main_list.find_all('ul', recursive=False)[1:]

        for sub_list in [main_list[0]]:
            sub_list = sub_list.find_all('li')

            for scp_element in sub_list[:5]:
                scp_element = scp_element.text
                scp_number = ''.join([l for l in scp_element.split(' - ')[0] if l.isnumeric()])
                scp_tag = ''.join(scp_element.split(' - ')[1:])
                doesnt_exist_tag = '[ACCESS DENIED]'
                if scp_tag != doesnt_exist_tag:
                    update_scp(scp_number, arg_scp_name=scp_tag)

                # delay time to make sure I don't overload their website with requests
                sleep(global_vars.delay_time_s)
