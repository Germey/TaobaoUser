## 淘宝用户抓取

### 项目简述

本项目用来抓取淘宝非匿名用户以及评论，通过淘宝宝贝下方的推荐商品抓取评论内容。抓取到到结果保存到excel中。  
由于淘宝采用大量JavaScript渲染以及Ajax，本项目采用Selenium＋Chrome来抓取相应内容，采用延时等待，模拟下拉点击等方法驱动浏览器渲染页面。  
项目提供了如下功能：

* 输入淘宝关键字采集淘宝链接并写入到文件
* 从文件读取链接，执行评论采集
* 将评论保存到Excel中，记录当前采集索引


### 项目说明

#### 安装

安装Python

```
Python 2.7 https://www.python.org
```
下载代码

```
git clone https://github.com/Germey/TaobaoUser.git
```

安装类库

```
pip install pyquery selenium twisted requests xlrd xlwt xlutils 
```

安装浏览器

```
安装Chrome浏览器，并下载Chromedriver将其到环境变量
```

#### 使用

首先采集链接

```
python get_links.py
```

从文件中批量读取链接并采集

```
python from_file.py
```
手动输入链接并采集

```
python from_input.py
```

#### 可配置项

项目中可配置项均位于 config.py 中

* URLS_FILE  

保存链接单的文件

* OUT_FILE  

输出文本EXCEL路径

* COUNT_TXT

计数文件

* DRIVER

浏览器驱动

* TIMEOUT

采集超时时间

* MAX_SCROLL_TIME

下拉滚动条最大次数

* NOW_URL_COUNT

当前采集到第几个链接

* LOGIN_URL

登录淘宝的链接

* SEARCH_LINK

采集淘宝链接搜索页面

* CONTENT

采集链接临时变量

* PAGE

采集淘宝链接翻页数目

* FILTER_SHOP

是否过滤相同店铺

* TOTAL_URLS_COUNT

爬取链接总数


### 教程讲解

[抓取淘宝匿名旺旺](http://cuiqingcai.com/2852.html)



