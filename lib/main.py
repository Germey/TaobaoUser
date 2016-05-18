# -*- coding:utf-8 -*-
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
from lib.get_recommends import get_recommends_infos
from lib.write_to_excel import repeat_excel, write_info

reload(sys)
sys.setdefaultencoding("utf-8")



def deal_recommends_infos(url):
    infos = get_recommends_infos(url)
    for info in infos:
        targets = []
        url = info.get('url')
        comments_info = info.get('comments_info')
        for comment_info in comments_info:
            comment_content = comment_info[0]
            comment_user = comment_info[1]
            print 'comment_user', comment_user
            if len(comments_info) > 0 and not repeat_excel(comment_user) and filter_star(comment_user):
                targets.append((comment_user, comment_content))
        if len(targets) > 0:
            success_users = find_comment_info(url, targets)
            print success_users
            for success_user in set(success_users):
                write_info(success_user)

















