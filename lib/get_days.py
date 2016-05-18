# -*- coding: utf-8 -*-


import time
import datetime


def get_day(pre_day = 1):

    #先获得时间数组格式的日期
    threeDayAgo = (datetime.datetime.now() - datetime.timedelta(days = pre_day))
    #转换为时间戳:
    timeStamp = int(time.mktime(threeDayAgo.timetuple()))
    #转换为其他字符串格式:
    otherStyleTime = threeDayAgo.strftime("%m.%d")

    return otherStyleTime



def get_days(max_day):
    dates = []
    for day in range(0, max_day):
        date = get_day(day)
        dates.append(date)

    return dates

if __name__ == "__main__":

    print get_days(10)
