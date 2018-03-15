# coding:utf8

from selenium import webdriver

browser = webdriver.Chrome()
browser.get(r'http://inventwithpython.com')
linkElem = browser.find_element_by_link_text('Read Online for Free')
print(linkElem)
linkElem.click()

input('Press any key to quit...')

browser.quit()
