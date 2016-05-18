# -*- coding: utf-8 -*-
from selenium import webdriver
import config
import copy

def new_driver():
    #service_args = copy.copy(config.SERVICE_ARGS)
    #config.DRIVER = webdriver.PhantomJS(service_args=service_args)
    config.DRIVER = webdriver.Chrome()