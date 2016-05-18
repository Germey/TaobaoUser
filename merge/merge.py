# -*- coding: utf-8 -*-
import xlrd
from xlutils.copy import copy

import config
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def merge_file():
    excel = config.OUT_FILE
    phone = config.PHONE_TXT
    rb = xlrd.open_workbook(excel)
    sheet = rb.sheets()[0]
    names = sheet.col_values(0)
    phone_txt = open(phone, 'r').read()
    phones = phone_txt.split('\n')
    phone_count = len(phones)
    # print phones
    wb = copy(rb)
    write_sheet = wb.get_sheet(0)
    success_count = 0
    count = 0
    valid_count = 0
    has_phone = 0
    print u'正在检测电话文本,请稍后'
    for phone in phones:
        info = phone.split(' ')
        if len(info) >= 2:
            has_phone = has_phone + 1

    success_people = []
    for name in names:
        name = name.strip()
        if name:
            valid_count = valid_count + 1
        count = count + 1
        print u'当前匹配第', count, u'行表格', name
        success = 0
        for phone in phones:
            info = phone.split(' ')
            if len(info) == 2:
                first = info[0].strip()
                second = info[1]
                if name.decode('utf-8', 'ignore') == first.decode('utf-8', 'ignore'):
                    success = 1
                    success_count = success_count + 1
                    success_people.append(name)
                    print u'当前成功匹配了', success_count, '位用户'
                    print u'匹配到用户', name
                    print u'电话号码', phone
                    if len(second) == 11:
                        write_sheet.write(count - 1, 7, second)
                        wb.save(excel)
                    else:
                        print u'电话号码信息不完整, 没有导入'

        if not success:
            print u'未找到匹配用户'

    print u'匹配结束,成功的用户有'
    for people in success_people:
        print people, ' ',
    print ''
    print u'匹配结束, Excel表中共有', count, u'行, 有效旺旺信息', valid_count, u'行, 电话文本共有', phone_count, u'行, 其中有电话号码信息的', has_phone, u'行, 共匹配了', success_count, u'位用户'
