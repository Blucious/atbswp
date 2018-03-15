# coding:utf8

from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome()
browser.get(r'https://nostarch.com/')

try:
    inputElem = browser.find_element_by_css_selector('input[placeholder="验证码"]')
    userInput = input(': ')
    inputElem.send_keys(userInput)
    inputElem.submit()
except common.exceptions.NoSuchElementException:
    pass

if browser.current_url == r'https://nostarch.com/':
    htmlElem = browser.find_element_by_tag_name('html')
    htmlElem.send_keys(Keys.END)
    htmlElem.send_keys(Keys.HOME)

# browser.back()
# browser.forward()
# browser.refresh()
# browser.quit()
















