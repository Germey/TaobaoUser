# -*- coding:utf-8 -*-
import re
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import xlrd
import xlwt
import config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from lib.filter_star import filter_star_by_user, filter_star
from lib.get_comments import find_comment_info
from lib.get_days import get_days
from xlutils.copy import copy
import sys
from lib.get_recommends import get_recommends_infos, deal_recommends_infos
from lib.get_urls import get_urls
from lib.write_to_excel import repeat_excel, write_info, get_count, write_count

reload(sys)
sys.setdefaultencoding("utf-8")


def scrap(url):
    deal_recommends_infos(url)


def from_input():
    url = raw_input('请输入宝贝链接:')
    scrap(url)
    print u'采集结束'


def from_file():
    urls = get_urls()
    print u'获取到如下链接列表'
    print urls
    config.TOTAL_URLS_COUNT = len(urls)
    print u'共有', config.TOTAL_URLS_COUNT, u'个链接'
    count = int(get_count())
    print u'上次爬取到第', int(count) + 1, u'个链接, 继续爬取'
    print u'输入 1 继续爬取,输入 2 重新爬取:'
    num = raw_input()
    if num == '2':
        count = 0
        print u'开始重新爬取'
    if count < config.TOTAL_URLS_COUNT:
        for count in range(count, config.TOTAL_URLS_COUNT):
            write_count(count, config.COUNT_TXT)
            url = urls[count]
            print u'正在爬取第', count+1, u'个网页, 共', config.TOTAL_URLS_COUNT, u'个'
            config.NOW_URL_COUNT = count
            scrap(url)
            count = count + 1
            print u'当前已完成采集', config.NOW_URL_COUNT + 1, u'个, 共', config.TOTAL_URLS_COUNT, u'个'
        print u'采集结束,完成了', len(urls), u'个链接的采集'
    else:
        print u'链接上次已经全部爬取完毕'














