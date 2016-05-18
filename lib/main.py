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


def is_recommends_appear(driver, max_time=10):
    count = 1
    result = scroll_bottom_recommends(driver)
    while not result:
        result = scroll_bottom_recommends(driver)
        count = count + 1
        if count == max_time:
            return False
    return True


def scroll_bottom_recommends(driver):
    js = "window.scrollTo(0,document.body.scrollHeight)"
    driver.execute_script(js)
    time.sleep(2)
    try:
        driver.find_element_by_css_selector('#J_TjWaterfall li')
    except NoSuchElementException:
        return False
    return True


def scrap_recommends_page(url):
    driver = config.DRIVER
    timeout = config.TIMEOUT
    max_scroll_time = config.MAX_SCROLL_TIME

    driver.get(url)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "J_TabRecommends"))
    )
    if is_recommends_appear(driver, max_scroll_time):
        return driver.page_source
    else:
        return False


def get_recommends_infos(url):
    info = []
    html = scrap_recommends_page(url)
    doc = pq(html)
    items = doc('#J_TjWaterfall > li')
    print items
    print u'在此宝贝推荐链接中找到如下用户评论:'
    for item in items.items():
        url = item.find('a').attr('href')
        comments_info = []
        comments = item.find('p').items()
        for comment in comments:
            comment_user = comment.find('b').remove().text()
            comment_content = comment.text()
            anonymous_str = config.ANONYMOUS_STR
            if not anonymous_str in comment_user:
                comments_info.append((comment_content, comment_user))
        info.append({'url': url, 'comments_info': comments_info})

    print info
    return info


def new_excel(file=config.OUT_FILE):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    book.add_sheet('sheet1', cell_overwrite_ok=True)
    book.save(file)
    print u'已成功创建文件', file


def repeat_excel(word, file=config.OUT_FILE):
    try:
        workbook = xlrd.open_workbook(file)
        sheet = workbook.sheet_by_index(0)
        words = sheet.col_values(0)
        if word in words:
            return True
        else:
            return False
    except IOError, e:
        if 'No such file' in e.strerror:
            print u'匹配重复时未找到该文件', file
            new_excel(file)
            return False
        return False


def filter_star(user, max_star=config.MAX_STAR):
    need_filter_star = config.FILTER_STAR
    if not need_filter_star:
        return True
    return filter_star_by_user(user)


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
                print u'出现日期不匹配，当前评论日期为', date
                config.WRONG_DATE_COUNT += 1
                print u'当前日期不匹配次数为', config.WRONG_DATE_COUNT
                if config.WRONG_DATE_COUNT > config.WRONG_DATE_MAX_COUNT:
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
        comment_text = comment[2]
        if target_user and len(target_user) >= 5:
            if equal_text(user[0], target_user[0]) and equal_text(user[4], target_user[-1]):
                print u'匹配到旺旺名', target_user
                return comment


def limit_comments_count(html):
    doc = pq(html)
    comments_count = doc('.J_ReviewsCount').eq(0).text()
    print comments_count
    if config.MAX_COMMENTS_LIMIT:
        if int(comments_count) > config.MAX_COMMENTS_COUNT:
            return False
        else:
            return True
    return True


def complete_url(url):
    if url.startswith('//'):
        url = 'https:' + url
    return url


def write_to_excel(contents, file=config.OUT_FILE):
    try:
        rb = xlrd.open_workbook(file)
        sheet = rb.sheets()[0]
        row = sheet.nrows
        wb = copy(rb)
        sheet = wb.get_sheet(0)
        count = 0
        name = contents[0]
        if not repeat_excel(name, file):
            for content in contents:
                sheet.write(row, count, content)
                count = count + 1
                wb.save(file)
                print u'已成功写入到文件', file, u'第', row + 1, u'行'
        else:
            print u'内容已存在, 跳过写入文件', file

    except IOError:
        print u'未找到该文件', file
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        book.add_sheet('sheet1', cell_overwrite_ok=True)
        book.save(file)
        print u'已成功创建该文件', file
        write_to_excel(contents, file)


def write_info(infos, file=config.OUT_FILE):
    name = infos[0]
    title = infos[1]
    url = infos[2]
    info = infos[3]
    date = info[1]
    comment = info[2]
    meta = info[3]
    contents = (name, date, comment, meta, title, url)
    write_to_excel(contents, file)


def get_title(html):
    doc = pq(html)
    title = doc('title').eq(0).text()
    if title:
        print title
        return title


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
    print success_users
    return success_users
