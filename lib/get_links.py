# -*- coding: utf-8 -*-
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from pyquery import PyQuery as pq
import config
import sys
import locale

reload(sys)
sys.setdefaultencoding("utf-8")

shop_list = []
link_list = []


def get_results(keyword):
    driver = config.DRIVER
    link = config.SEARCH_LINK
    driver.get(link)
    try:
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "mq"))
        )
    except TimeoutException:
        print u'加载页面失败'
    try:
        element = driver.find_element_by_css_selector('#mq')
        print u'成功找到了搜索框'
        keyword = keyword.decode('utf-8', 'ignore')
        print keyword
        print u'输入关键字', keyword
        for word in keyword:
            print word
            element.send_keys(word)
        element.send_keys(Keys.ENTER)
    except NoSuchElementException:
        print u'没有找到搜索框'
    print u'正在查询该关键字'
    try:
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_ItemList div.productImg-wrap"))
        )
    except TimeoutException:
        print u'查询失败'
    html = driver.page_source
    return html


def parse_html(html):
    doc = pq(html)
    products = doc('#J_ItemList .product').items()
    for product in products:
        shop = product.find('.productShop-name').text()
        href = product.find('.productImg').attr('href')
        if shop and href:
            if config.FILTER_SHOP:
                if not shop in shop_list:
                    href = 'https:' + href
                    print shop, href
                    shop_list.append(shop)
                    link_list.append(href)
                    write_file(href)
                    print u'当前已采集', len(shop_list), u'个链接'
                else:
                    print u'店铺', shop, u'已经存在'
            else:
                shop_list.append(shop)
                link_list.append(href)
                write_file(href)
                print u'当前已采集', len(shop_list), u'个链接'


def get_more_link():
    print u'正在采集下一页的宝贝链接'
    driver = config.DRIVER
    try:
        js = "window.scrollTo(0,document.body.scrollHeight)"
        driver.execute_script(js)
    except WebDriverException:
        print u'页面下拉失败'
    try:
        next = driver.find_element_by_css_selector('#content b.ui-page-num > a.ui-page-next')
        next.click()
    except NoSuchElementException:
        print u'找到了翻页按钮'
    driver.implicitly_wait(5)
    try:
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_ItemList div.productImg-wrap"))
        )
    except TimeoutException:
        print u'查询失败'
    html = driver.page_source
    parse_html(html)


def find_urls():
    print u'请输入要提取链接的关键字'
    keyword = raw_input().decode(sys.stdin.encoding or locale.getpreferredencoding(True))
    
    print u'您要提取的关键字是', keyword
    print u'正在开始提取...'
    try:
        clear_file()
        html = get_results(keyword)
        parse_html(html)
        for i in range(1, config.PAGE + 1):
            print u'当前第',(i-1), u'页'
            get_more_link()
    except Exception:
        print u'网络错误，请重试'

        with open(config.URLS_FILE, 'w') as f:
            f.write(config.CONTENT)
            f.close()
            print u'出现异常，已还原原内容'
    finally:
        config.DRIVER.close()
        print u'采集结束, 共采集', len(link_list), u'个链接'


def write_file(href):
    try:
        with open(config.URLS_FILE, 'a') as f:
            f.write(href + '\n')
            f.close()
    except Exception:
        print u'写入失败'


def clear_file():
    try:
        with open(config.URLS_FILE, 'r') as f:
            config.CONTENT = f.read()
            print config.CONTENT
            f.close()
        print u'正在清空爬取链接，等待重新爬取新链接'
        with open(config.URLS_FILE, 'w') as f:
            f.write('')
            f.close()
    except Exception:
        print u'清空链接失败'
