# -*- coding:utf-8 -*-
import re
import config


def get_urls():
    try:
        file = open(config.URLS_FILE, 'r')
        content = file.read()
        #print content
        pattern = re.compile(r'(.*?//.*?)\s', re.S)
        urls = re.findall(pattern, content)
        return urls

    except Exception, e:
        print u'获取链接失败', e.message