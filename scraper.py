"""
This is the web scraper, which handles all data gathering from the wiki.
"""

from time import sleep
import requests
from bs4 import BeautifulSoup
from webbrowser import open as wp_open

import cfg
import global_vars


class WikiScraper():
    def __init__(self):
        pass

    def request_wrapper(self, URL, headers):
        """
        Wrapper for requests.get()
        does some necessary extra things each time a request is made.
        """
        if global_vars.delay_time_ms:
            sleep(global_vars.delay_time_ms / 1000)

        request_result = requests.get(URL, headers)
        global_vars.requests_count += 1

        return request_result

    def get_scp_series_links(self):
        """
        The wiki groups 1000 SPCs together per page.
        This function scrapes the homepage of the wiki to get links to those pages.
        """
        main_source = self.request_wrapper(cfg.HOMEPAGE_URL, headers=cfg.HEADERS)

        main_soup = BeautifulSoup(main_source.text, 'lxml')
        scp_series_menu = main_soup.find_all('div', class_='menu-item')[1]
        scp_series_anchors = scp_series_menu.find_all('a')

        scp_series_links = []
        for i in scp_series_anchors:
            path_link = str(i).split('"')[1]
            full_link = cfg.HOMEPAGE_URL + path_link[1:]
            scp_series_links.append(full_link)

        return scp_series_links

    def reformat_scp_num(self, scp_number:int):
        """
        Reformats an int to a string with an appropriate amount of leading zeros.
        This is necessary to correctly construct some URLs.
        """
        str_number = str(scp_number)
        while (len(str_number)) < 3:
            str_number = '0' + str_number
        return str_number

    def go_to_scp_page(self, scp_number):
        """
        Opens the SCP's webpage in a webbrowser.
        """
        str_number = self.reformat_scp_num(scp_number)
        URL = cfg.HOMEPAGE_URL + 'scp-' + str_number
        wp_open(URL, new=2)


