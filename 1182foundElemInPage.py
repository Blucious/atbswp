# coding:utf8

import selenium
from selenium import webdriver, common

browser = webdriver.Chrome()
browser.get('http://inventwithpython.com/')
try:
    elem = browser.find_element_by_class_name('card')
    print('Found <%s> element with that class name!' % elem.tag_name)
except common.exceptions.NoSuchElementException as err:
    print('Was not able to find an element with that name.\nDetails:%s' % str(err))

browser.quit()
