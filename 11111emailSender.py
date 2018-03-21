# coding:utf8

"""Usage:emailSender.py <address> <text>
使用指定账户，登入网易邮箱发送邮件。
"""

import re
import sys
import traceback

from selenium import webdriver
from selenium import common
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC

REGEX_EMAIL_ADDRESS_FORMAT = re.compile(r'^[\w.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$')


EMAIL_URL = r'https://mail.163.com/'
# ---------------------------------------------------
USER_NAME = r''
USER_PASSWORD = r''
# ---------------------------------------------------


# def _1(s):
#     r = ''
#     for i in range(len(s)):
#         r += chr(ord(s[i]) ^ 0xffff)
#     return r


if len(sys.argv) == 3:
    if not REGEX_EMAIL_ADDRESS_FORMAT.match(sys.argv[1]):
        print('Invalid email address')
        sys.exit()

    try:
        # chromeOptions = webdriver.ChromeOptions()
        # chromeOptions.add_argument('--headless')
        driver = webdriver.Chrome()
    except common.exceptions.WebDriverException as err:
        print(err)
        sys.exit()

    try:
        driver.implicitly_wait(10)

        driver.get(EMAIL_URL)

        ActionChains(driver).move_to_element(driver.find_element_by_id('lbNormal')).perform()

        # 填写用户名密码
        driver.switch_to.frame(driver.find_element_by_id('x-URS-iframe'))
        driver.find_element_by_name('email').send_keys(USER_NAME)
        driver.find_element_by_name('password').send_keys(USER_PASSWORD)

        # 单击登入按钮
        driver.find_element_by_id('dologin').click()
        while True:
            try:
                # 单击写信按钮
                driver.find_element_by_css_selector('#_mail_component_68_68').click()
            except common.exceptions.NoSuchElementException:
                print('Waiting for manual verification and click sign-in...')
            else:
                break

        # 填写收件人
        driver.find_element_by_class_name('nui-editableAddr-ipt').send_keys(sys.argv[1])

        # 填写内容
        driver.switch_to.frame(driver.find_element_by_class_name('APP-editor-iframe'))
        driver.find_element_by_class_name('nui-scroll').send_keys(sys.argv[2])

        # 发送
        driver.switch_to.parent_frame()
        driver.find_element_by_css_selector('footer>div').click()
        driver.find_element_by_css_selector('div[class="nui-msgbox-ft-btns"]>div').click()

        # 等待发送成功
        WebDriverWait(driver, 10).until(lambda d: d.find_element_by_css_selector('h1[class="tK1"]>b'))
        print('All done')

        # input('Press any key to quit...')

    except (Exception, ):
        traceback.print_exc()
    finally:
        driver.quit()

else:
    print(__doc__)


