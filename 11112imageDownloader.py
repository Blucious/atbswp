# coding:utf8

"""imageDownloader.py <keyword> <npages> [options]
Description:
    download video covers from www.bilibili.com

Example:
    imageDownloader.py python 2
    imageDownloader.py python 2 --max_workers 5 --target-dir ./image
"""

#                                                       |   |
#                                                     |   | |
# ProcedureParsePage                        ProcedureDonwloadImage
#    |   |              Queue                       |   | | |...
#    |   |--<pageURL>-->|   |--<imageURL/pageURL>-->|   | | |
#    |   |              |   |<------<imageURL>------|   | |
#    |   |                                          |   |
#


import os
import sys
import time
import queue
import threading

import requests

from re import compile as _re_compile
from urllib.parse import urlencode as _urlencode
from selenium import webdriver
from selenium import common

REGEX_SEARCH_IMAGE = _re_compile(r'<meta data-vue-meta="true" itemprop="image" content="([^"]+)"/>')
REGEX_VIDEO_IDENT = _re_compile(r'av\d+')

DICT_HEADERS = {
    'User-Agent': 'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)'
                  'AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'
}

STRING_URL_BASE = 'https://search.bilibili.com/all?'
EVENT_ALL_DONE = threading.Event()

INT_TIME_OUT = 12


class MyThread(threading.Thread):
    _RES_NONE = object()

    def __init__(self, cls, args=None, kwargs=None):
        threading.Thread.__init__(self)
        self.cls = cls
        self.args = args if args else tuple()
        self.kwargs = kwargs if kwargs else dict()
        self.result = self._RES_NONE

    def get_result(self):
        if self.result is self._RES_NONE:
            raise RuntimeError('call get_result() before run')
        return self.result

    def run(self):
        print('[+]Thread %d starting at %s' % (self.ident, time.ctime()))
        self.result = self.cls(*self.args, **self.kwargs)()
        print('[+]Thread %d finished at %s' % (self.ident, time.ctime()))


def download(url, params=None, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = INT_TIME_OUT
    if 'headers' not in kwargs:
        kwargs['headers'] = DICT_HEADERS
    response = None
    try:
        response = requests.get(url, params=params, **kwargs)
        response.raise_for_status()
    except Exception as err:
        print('[-]Error: %s' % err)
    return response


class ProcedureDonwloadImage:
    _TimeOutNumberForExit = 3
    _QueueEmptyTimeOut = 7
    _ReqFnMapping = dict()

    def __init__(self, download_dir, url_queue):
        self._urlQueue = url_queue
        self._rootDir = download_dir
        # self._threadId = threading.get_ident()

    def __call__(self):
        self.make_directory()
        timeOutCount = 0
        while True:
            # print('[?]id %d' % threading.get_ident(), EVENT_ALL_DONE.is_set(), isTimeOut, self._urlQueue.qsize())
            if EVENT_ALL_DONE.is_set() and self._urlQueue.empty() or \
                    timeOutCount >= self._TimeOutNumberForExit:
                break

            try:
                reqTuple = self._urlQueue.get(True, self._QueueEmptyTimeOut)
                assert reqTuple[0] in self._ReqFnMapping

                print('[+]Get: %s, Remaining count: %d' % (str(reqTuple), self._urlQueue.qsize()))

                response = download(reqTuple[1])
                if response:
                    print('[+]Download finished: %s' % reqTuple[1])
                    self._ReqFnMapping[reqTuple[0]](self, reqTuple, response)
                else:
                    print('[-]Download failed: %s' % reqTuple[1])
            except queue.Empty:
                timeOutCount += 1
                print('[?]Time out, Count %d, Thread exits when the timeout counts greater than or equal to %d' %
                      (timeOutCount, self._TimeOutNumberForExit))
            except Exception as err:
                print('[-]Error: %s' % err)

    # req_tup: ('image', <url>, <videoIdent>)
    def _req_image(self, req_tup, response):
        if not req_tup[2]:
            fileName = req_tup[1].split('/')[-1]
        else:
            fileName = '%s.%s' % (req_tup[2], req_tup[1].split('.')[-1])
        self.save_file_by_response(fileName, response)

    _ReqFnMapping['image'] = _req_image

    # req_tup: ('page', <url>)
    def _req_page(self, req_tup, response):
        imageURLMatchObj = REGEX_SEARCH_IMAGE.search(response.text)
        if imageURLMatchObj:
            videoIdentMatchObj = REGEX_VIDEO_IDENT.search(response.url)
            videoIdent = videoIdentMatchObj.group() if videoIdentMatchObj else ''
            newReqTuple = ('image', imageURLMatchObj.group(1), videoIdent)
            self._urlQueue.put(newReqTuple)
            print('[+]Put: %s' % str(newReqTuple))
        else:
            print('[-]Image URL not found on page %s' % req_tup[1])

    _ReqFnMapping['page'] = _req_page

    def make_directory(self):
        os.makedirs(self._rootDir, exist_ok=True)

    def save_file_by_response(self, filename, response):
        filename = os.path.join(self._rootDir, filename)
        if os.path.exists(filename):
            print('[=]File has existed: %s' % filename)
        else:
            with open(filename, 'wb') as binFile:
                for chunk in response.iter_content(0xffff):
                    binFile.write(chunk)


class ProcedureParsePage:
    def __init__(self, keyword, num_pages, url_queue):
        self._urlQueue = url_queue
        self._numberOfPages = num_pages
        self._keyword = keyword

    def __call__(self):
        successFlag = True
        try:
            self._driver = webdriver.Chrome()
            self._driver.implicitly_wait(4)
            try:
                lastPage = self.get_last_page()
                if lastPage == -1:
                    successFlag = False
                else:
                    for i in range(1, min(self._numberOfPages, lastPage) + 1):
                        url = STRING_URL_BASE + _urlencode({'keyword': self._keyword, 'page': str(i)})
                        print('[+]Page %d downloading...' % i)
                        flag = self.collect_url_in_page(url)
                        if flag:
                            print('[+]Page %d download completed' % i)
                        else:
                            print('[-]Page %d download failed' % i)
            finally:
                self._driver.quit()
        except common.exceptions.WebDriverException as err:
            print('[-]Error: %s' % err)
        finally:
            EVENT_ALL_DONE.set()

        return successFlag

    def collect_url_in_page(self, url) -> bool:
        try:
            self._driver.get(url)
            aElems = self._driver.find_elements_by_css_selector('li[class="video matrix"]>a')
            for aElem in aElems:
                pageURL = aElem.get_attribute('href')
                reqTuple = ('page', pageURL)
                self._urlQueue.put(reqTuple)
                print('[+]Put: %s' % str(reqTuple))
            return True
        except Exception as err:
            print('[-]Error: %s, %s' % (type(err), err))
        return False

    def get_last_page(self) -> int:
        try:
            url = STRING_URL_BASE + _urlencode({'keyword': self._keyword, 'page': '1'})
            self._driver.get(url)
            buttonElem = self._driver.find_element_by_css_selector('li[class="page-item last"]>button')
            return int(buttonElem.text)
        except common.exceptions.NoSuchElementException:
            print('[-]No result: %s' % self._keyword)
        except Exception as err:
            print('[-]Error: %s, %s' % (type(err), err))
        return -1


def main():
    import optparse

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option('-m', '--max-workers', dest='max_workers', type='int', default=3,
                      help='The number of procedures to download page & image [default: %default]')
    parser.add_option('-t', '--target-dir', dest='target_dir', type='string', default='img',
                      help='Target directory [default: %default]')
    opts, args = parser.parse_args()

    if len(args) != 2:
        parser.error('incorrect number of arguments')
        return 2
    # --- arg: <keyword> ---
    keyword = args[0]
    # --- arg: <numOfPages> ---
    if not args[1].isdigit():
        parser.error("invalid number '%s'" % args[1])
        return 2
    numOfPages = int(args[1])
    # --- option: --max-workers ---
    maxWorkers = min(max(opts.max_workers, 1), 20)
    # --- option: --target-dir ---
    table = str.maketrans({c: '_' for c in r'\/:*?"<>|'})
    targetDir = os.path.join(opts.target_dir.translate(table),
                             keyword.translate(table))

    # --- Process ---
    urlQueue = queue.Queue()
    threads = list()

    startTime = time.time()
    threads.append(MyThread(cls=ProcedureParsePage, args=(keyword, numOfPages, urlQueue)))
    for i in range(maxWorkers):
        threads.append(MyThread(cls=ProcedureDonwloadImage, args=(targetDir, urlQueue)))

    for i in range(len(threads)):
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    print('[+]all DONE, Costs: %f' % (time.time() - startTime))
    return None


if __name__ == '__main__':
    sys.exit(main())
