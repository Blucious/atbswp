# coding:utf8

from selenium import webdriver

browser = webdriver.Chrome()
browser.get(r'https://www.zhihu.com/signup?next=%2F')

# 查找登录按钮，单击
signInElem = browser.find_element_by_css_selector('span[data-reactid="93"]')
signInElem.click()

# 查找输入框
userNameOrEmailInputElem = browser.find_element_by_css_selector('input[name="username"]')
userNameOrEmailInputElem.send_keys('12345')

# 填写内容
passwordInputElem = browser.find_element_by_css_selector('input[name="password"]')
passwordInputElem.send_keys('12345')

# 提交表单
passwordInputElem.submit()  # 在任何元素上调用submit()方法，都等同于点击该元素所在表单的Submit按钮

# 由于要进行验证，无法实现自动登入

input('Press any key to quit...')

browser.quit()














