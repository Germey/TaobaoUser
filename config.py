# -*- coding:utf-8 -*-
from selenium import webdriver

URLS_FILE = 'file/urls.txt'

OUT_FILE = 'file/result.xls'

COUNT_TXT = 'file/count.txt'

DRIVER = webdriver.Chrome()

TIMEOUT = 30

MAX_SCROLL_TIME = 10

TOTAL_URLS_COUNT = 0

NOW_URL_COUNT = 0

LOGIN_URL = 'https://login.taobao.com/member/login.jhtml?spm=a21bo.50862.754894437.1.MVF6jc&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F'

SEARCH_LINK = 'https://www.tmall.com/?spm=a220m.1000858.a2226n0.1.kM59nz'

CONTENT = ''

PAGE = 25

FILTER_SHOP = False

ANONYMOUS_STR = '***'