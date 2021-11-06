from bs4 import BeautifulSoup
import requests
from webbrowser import open as wp_open
from random import choice
from time import sleep

from scp import SCP
import db
import global_vars
import cfg
import scraper

ORM = db.SCPDatabase(cfg.DB_NAME)
scraper = scraper.WikiScraper()


def update_scp(scp_number):
    """
    Scrapes the wiki to find all desired data about an SCP.
    """
    str_number = scraper.reformat_scp_num(scp_number)
    scp_link = f'http://www.scp-wiki.net/scp-{str_number}'

    source = scraper.request_wrapper(scp_link, headers=cfg.HEADERS)
    soup = BeautifulSoup(source.text, 'lxml')

    # check whether SCP page exists
    try:
        exists_check = soup.find('h1', id='toc0').text
        if exists_check == "This page doesn't exist yet!":
            print("SCP doesn't exist yet!")
            # Even if the SCP doesn't exist we add it to the database as non-existent.
            # This allows us to fill the database with info on all scps later.
            new_scp = SCP(scp_number, "N/A", "N/A", "N/A", "N/A", 0, exists=0)
            result = ORM.add_scp(new_scp)
            if result == -1:
                ORM.update_scp(new_scp)
            return
    except AttributeError:
        pass

    # Sets series_index based on the first number of the scp.
    # This is needed for the code below.
    if len(str_number) < 4:
        series_index = 0
    else:
        series_index = int(str_number[0])

    # This makes it so that we only get the series links once any time
    # the program is run. This avoids sending unnecessary requests to the server.
    if global_vars.series_links is None:
        global_vars.series_links = scraper.get_scp_series_links()

    # The SCPs are bunched together in groups of 1000 called a "series".
    # This fetches the source content for the series that this scp is located at,
    # which is the only place we can find its name. If this specific
    # series source was not already requested we do that now - then we store it in
    # memory until the program is terminated to avoid unecessary requests in the future
    if global_vars.series_sources.get(series_index) is None:
        global_vars.series_sources[series_index] = scraper.request_wrapper(
            global_vars.series_links[series_index], headers=cfg.HEADERS
        )
    series_source = global_vars.series_sources[series_index]

    # Gets the name of the SCP (only accessible via the SCP series links)
    scp_list_index = int(str_number[-2:])
    main_list_index = int(str_number[-3])
    series_soup = BeautifulSoup(series_source.text, 'lxml')
    scp_names_sublist = series_soup.find(
        'div', class_='content-panel standalone series'
    ).select('ul')[main_list_index + 1].find_all('li')
    # this offset is used to find the correct place on the html where the name is listed
    offset = 0
    if int(str_number) < 100:
        # Usually the scps least significant digit starts counting at 0 in each 
        # grouping. However, for the first grouping (001-099), the least significant 
        # digit starts at 1, so we must account for this in our offset to find the 
        # correct name
        offset = -1
    name = ' - '.join(scp_names_sublist[scp_list_index + offset].text.split(" - ")[1:])

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

    # Check whether the SCP has an unusual format (such as SCP 2000 and 2521).
    # SCPs with unusual format will be given "Unknown" as their object_class and
    # False for has_image.
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

    # Finds the SCP's object class.
    # object_class = "Unknown" by default if it's format is unusual.
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

    # Tries to add the scp to the database and gets the 
    # result of whether it was successful
    result = ORM.add_scp(new_scp)
    if result == -1:
        # This block will run if the scp is already in the database.
        # In this case we want to update it with the current data.
        ORM.update_scp(new_scp)
        # 2 indicates that the scp was updated
        return 2
    # 1 indicates that the SCP was added
    return 1
