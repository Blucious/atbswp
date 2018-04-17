# coding:utf8

import sys
import logging
from selenium import common
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait as By
# from selenium.webdriver.support import expected_conditions as EC


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

fmt = logging.Formatter(fmt='%(levelname)s: %(lineno)d, %(message)s')
stream = logging.StreamHandler(stream=sys.stdout)
stream.setFormatter(fmt)
del fmt
_logger.addHandler(stream)
del stream


def next_step_getter():
    _stepTuple = (Keys.UP, Keys.RIGHT, Keys.DOWN, Keys.LEFT)
    _index = 0

    def getter():
        nonlocal _index
        _index = (_index + 1) % len(_stepTuple)
        return _stepTuple[_index]
    return getter


class Auto2048:
    def __init__(self):
        self.browser = webdriver.Chrome()  # 'chromedriver.exe' is required

    def run(self):
        try:
            self.browser.get('https://gabrielecirulli.github.io/2048/')

            htmlElem = self.browser.find_element_by_tag_name('html')
            getter = next_step_getter()

            # -------------------- loop --------------------
            while not self.game_over():
                htmlElem.send_keys(getter())
            _logger.info('End of loop')

        except BaseException as err:
            raise err
        finally:
            input('Press any key to quit...')
            self.browser.quit()
            _logger.info('All done.')

    def game_over(self) -> bool:
        try:
            self.browser.find_element_by_css_selector('[class*="game-over"]')
        except common.exceptions.NoSuchElementException:
            return False
        return True


if __name__ == '__main__':
    a2 = Auto2048()
    a2.run()
