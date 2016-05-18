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
from lib.filter_star import filter_star_by_user
from lib.get_days import get_days
from xlutils.copy import copy
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def get_title(html):
    doc = pq(html)
    title = doc('title').eq(0).text()
    if title:
        return title


def complete_url(url):
    if url.startswith('//'):
        url = 'https:' + url
    return url


def find_comment_info(url, targets):
    driver = config.DRIVER
    timeout = config.TIMEOUT
    success_users = set([])
    print '正在匹配评论', url
    url = complete_url(url)
    config.NEXT_PAGE_COMMENTS = 1
    driver.get(url)
    title = ''
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "J_TabBar"))
        )
    except TimeoutException:
        print u'请求匹配评论页面超时'
    if is_comments_appear(driver):
        print u'已成功加载出评论页面'
        config.WRONG_DATE_COUNT = 0
        js = '''
        comment_btn = document.querySelectorAll('#J_TabBar li a')[1]
        comment_btn.click()
        '''
        try:
            driver.execute_script(js)
        except WebDriverException:
            print u'点击获取评论按钮失败'
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-author"))
            )
        except TimeoutException:
            print u'请求匹配评论页面超时'
        html = driver.page_source
        title = get_title(html)
        print u'该宝贝名称是', title
        if not limit_comments_count(html):
            return None
        comments = parse_comments(html)
        for target in targets:
            target_user = target[0]
            target_content = target[1]
            comment = filter_comments(comments, target_user, target_content)
            if comment:
                success_users.add((target_user, title, url, comment))
    page_count = 1
    while config.NEXT_PAGE_COMMENTS:
        print u'正在分析后续评论'
        try:
            js = '''
            page = document.querySelectorAll('.rate-paginator a');
            length = page.length;
            a = page[length-1];
            a.click();
            '''
            try:
                driver.execute_script(js)
            except WebDriverException:
                print u'评论数目少，无需翻页'
                break
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "col-author"))
                )
            except TimeoutException:
                print u'请求匹配评论页面超时'
            driver.implicitly_wait(config.NEXT_PAGE_WAIT)
            html = driver.page_source
            comments = parse_comments(html)
            for target in targets:
                target_user = target[0]
                target_content = target[1]
                comment = filter_comments(comments, target_user, target_content)
                if comment:
                    success_users.add((target_user, title, url, comment))
            page_count += 1
            print u'已经匹配评论页数', page_count, u'次'
            time.sleep(1)
        except UnicodeDecodeError:
            print  u'匹配结果错误，跳过此匹配'
        except TimeoutException:
            print u'翻页失败'
    if len(success_users)>0:
        print u'该宝贝匹配到了用户'
        try:
            for success_user in success_users:
                print success_user[0]
        except Exception:
            print u'展示匹配到的用户失败'
    else:
        print u'该宝贝没有匹配到有效的旺旺'
    return success_users


def is_comments_appear(driver, max_time=10):
    count = 1
    result = scroll_bottom_comments(driver)
    while not result:
        result = scroll_bottom_comments(driver)
        count = count + 1
        if count == max_time:
            return False
    return True


def scroll_bottom_comments(driver):
    js = "window.scrollTo(0,document.body.scrollHeight)"
    driver.execute_script(js)
    time.sleep(2)
    try:
        driver.find_element_by_css_selector('#J_TabBar li a')
    except NoSuchElementException:
        return False
    return True


def parse_comments(html):
    doc = pq(html)
    lis = doc('.rate-grid tr')
    dates = get_days(config.MAX_DAY)
    comments = []
    for li in lis.items():
        date = li.find('.tm-rate-date').text()
        comment_text = li.find('.tm-rate-fulltxt').text()
        meta = li.find('.col-meta').text()
        user = li.find('.rate-user-info').text().replace(' ', '')[0:5]
        filter_date = config.FILTER_DATE
        if filter_date:
            if date in dates or date == u'今天':
                comments.append((user, date, comment_text, meta))
            else:
                print u'出现日期不符合的评论，当前评论日期为', date
                config.WRONG_DATE_COUNT += 1
                if config.WRONG_DATE_COUNT > config.WRONG_DATE_MAX_COUNT:
                    print u'当前不符合日期过多，不符合日期数是', config.WRONG_DATE_COUNT, u'，目前评论日期已到', date, u'旺旺号过于久远，直接跳过查询'
                    config.NEXT_PAGE_COMMENTS = 0
        else:
            comments.append((user, date, comment_text, meta))
    return comments


def equal_text(a, b):
    if a.decode('utf-8', 'ignore') == b.decode('utf-8', 'ignore'):
        return True
    return False


def filter_comments(comments, target_user=None, target_content=None):
    for comment in comments:
        user = comment[0]
        # comment_text = comment[2]
        if target_user and len(target_user) >= 5:
            if equal_text(user[0], target_user[0]) and equal_text(user[4], target_user[-1]):
                print u'匹配到旺旺名', target_user
                return comment


def limit_comments_count(html):
    print u'正在解析该宝贝评论数目'
    doc = pq(html)
    comments_count = doc('.J_ReviewsCount').eq(0).text()
    print u'该宝贝有', comments_count, u'条评论'
    if config.MAX_COMMENTS_LIMIT:
        if int(comments_count) > config.MAX_COMMENTS_COUNT:
            return False
        else:
            return True
    return True
