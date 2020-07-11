from bs4 import BeautifulSoup
import requests
from random import randint
from webbrowser import open as wp_open
from time import sleep
from datetime import datetime

from classes import SCP
from constants import headers, homepage_URL
import db
import global_vars


# todo refactor to search database instead of old dict
# def debug_display_scps(start=1, end=5, display_all=False, include_debug_info=False):
#     if display_all:
#         for scp_number in SCPs.keys():
#             display_scp(SCPs[scp_number].number, debug=include_debug_info)
#             print('')
#     else:
#         for i in range(start, end+1):
#             display_scp(i, debug=include_debug_info)
#             print('')


def debug_display_requests_count():
    print(f'{global_vars.debug_requests_count - global_vars.debug_requests_count_last} requests sent.')
    print(f'{global_vars.debug_requests_count} requests sent in total.')
    global_vars.debug_requests_count_last = global_vars.debug_requests_count


def reformat_SCP_num(scp_number):
    str_number = str(scp_number)
    while (len(str_number)) < 3:
        str_number = '0' + str_number
    return str_number


def get_scp_series_links():
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
    # SCPs with unusual format will be given None as their object class, and False for has_image
    str_number = reformat_SCP_num(scp_number)
    scp_link = f'http://www.scp-wiki.net/scp-{scp_number}'
    source = requests.get(scp_link, headers=headers)                        # request
    global_vars.debug_requests_count += 1
    soup = BeautifulSoup(source.text, 'lxml')


    # check whether SCP page exists
    try:
        exists_check = soup.find('h1', id='toc0').text
        if exists_check == "This page doesn't exist yet!":
            # SCPs[str_number] = SCP(str_number, None, None, None, scp_link, False, False, exists=False)
            print("SCP doesn't exist yet!")
            # todo refactor so scp gets stored in database as non-existent
            return
    except AttributeError:
        exists = 1

    if arg_scp_name:
        name = arg_scp_name
    else:
        if len(str_number) < 4:                                             # Gets the name of the SCP if not supplied via
            series_link = get_scp_series_links()[0]                         # argument (only accessible via the SCP series
        else:                                                               # links otherwise)
            series_link = get_scp_series_links()[int(str_number[0])]
        scp_list_index = int(str_number[-2:])
        main_list_index = int(str_number[-3])
        series_source = requests.get(series_link, headers=headers)          # request
        global_vars.debug_requests_count += 1
        series_soup = BeautifulSoup(series_source.text, 'lxml')
        scp_names_sublist = series_soup.find('div', class_='content-panel standalone series').select('ul')[main_list_index + 1].find_all('li')
        name = ' - '.join(scp_names_sublist[scp_list_index].text.split(" - ")[1:])

    page_content = soup.find('div', id='page-content')

    try:
        rating = page_content.find('span', class_='number prw54353').text   # find the SCP's rating
        rating = ''.join([l for l in rating if l.isnumeric()])
    except AttributeError:
        # This value is stored as a string in the db
        rating = "Unknown"

    try:                                                                # checks whether the SCP has an image
        has_image = int(bool(page_content.find_all('div', recursive=False)[1].img))
    except IndexError:                                                  # has_image = False by deault as a catch-all
        has_image = 0

    unusual_format = 0                                                  # check whether the SCP has an unusual format
    try:                                                                # such as SCP 2000 and 2521
        if has_image:
            if page_content.select('p')[1].text.split(' ')[0] != 'Item':
                unusual_format = 1
        else:
            if page_content.select('p')[0].text.split(' ')[0] != 'Item':
                unusual_format = 1
    except IndexError:
        unusual_format = 1

    if not unusual_format:                                              # finds the SCP's object class
        if has_image:                                                   # class = None by default if it's format
            object_class = page_content.find_all('p')[2].text           # is unnusual
            object_class = ' '.join(object_class.split(' ')[2:])
        else:
            object_class = page_content.find_all('p')[1].text
            object_class = object_class.split(' ')[2]
    else:
        object_class = "Unknown"

    # get the current day and store it in the format "DD-MM-YYYY"
    now = datetime.now()
    last_updated = f"{now.day}-{now.month}-{now.year}"

    # construct an SCP object from the data
    new_scp = SCP(scp_number, name, object_class, rating, scp_link, has_image,
                  unusual_format=unusual_format, last_updated=last_updated)

    # tries to add the scp to the database and gets the result of whether it was successful
    result = db.add_scp(new_scp)
    if result == -1:
        # this block will run if the scp is already in the database
        # todo add in a condition
        pass


def display_scp(scp_number, debug=False):
    # str_number = reformat_SCP_num(scp_number)
    scp = db.get_scp(scp_number)
    if scp == -1:
        print(f"SCP-{scp_number} not in database!")
    else:
        scp.display(debug=debug)


def go_to_scp_page(scp_number):
    URL = homepage_URL + 'scp-' + str(scp_number)
    wp_open(URL, new=2)


# todo refactor below functions to search database instead of old dict
# def give_random_scp(not_read_yet=True):
#     highest_SCP_num = max(int(k) for k in SCPs.keys())
#     while True:
#         try:
#             rand_SCP_int = randint(1, highest_SCP_num + 1)
#             SCP_key = reformat_SCP_num(rand_SCP_int)
#             if not_read_yet and SCPs[SCP_key].have_read == True:
#                 pass
#             else:
#                 return SCPs[SCP_key]
#         except KeyError:
#             pass
#
#
# def mark_scp_read_status(scp_number, have_read=True):
#     str_number = reformat_SCP_num(scp_number)
#     try:
#         SCPs[str_number].have_read = have_read
#     except KeyError:
#         print('SCP not in dictionary!')
#
#
# def mark_scp_dont_want_to_read_status(scp_number, dont_want_to_read=True):
#     str_number = reformat_SCP_num(scp_number)
#     try:
#         SCPs[str_number].dont_want_to_read = dont_want_to_read
#     except KeyError:
#         print('SCP not in dictionary!')


# todo functions to implement


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

                sleep(global_vars.delay_time_s)   # delay time to make sure I don't overload their website with requests


def display_top_scps(number):
    pass


