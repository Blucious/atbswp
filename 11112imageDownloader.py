# coding:utf8

"""imageDownloader.py
Description:
    download video covers from www.bilibili.com

Example:
    imageDownloader.py python 2
    imageDownloader.py python 2 --max_workers 5 --target-dir ./image
"""
#                                                       |   |
#                                                     |   | |
# ProcedurePageParser                        ProcedureDownloader
#    |   |              Queue                       |   | | |...
#    |   |--<pageURL>-->|   |--<imageURL/pageURL>-->|   | | |
#    |   |              |   |<------<imageURL>------|   | |
#    |   |                                          |   |


import os
import sys
import time
import queue
import atexit
import logging
import requests
import threading

from re import compile as _re_compile
from urllib.parse import quote as _quote
from urllib.parse import urlencode as _urlencode
from selenium import webdriver
from selenium import common

###############################################################################
__log__ = logging.getLogger(__name__)
__log__.setLevel(logging.DEBUG)

f = logging.Formatter('%(relativeCreated)d, %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(f)
fh = logging.FileHandler(filename='11112.log', mode='w', encoding='utf8')
fh.setFormatter(f)

__log__.addHandler(sh)
__log__.addHandler(fh)
del f
del sh
del fh

###############################################################################

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
    __resNone = object()

    def __init__(self, cls, args=None, kwargs=None, daemon=False):
        threading.Thread.__init__(self, daemon=daemon)
        self.cls = cls
        self.args = args if args else tuple()
        self.kwargs = kwargs if kwargs else dict()
        self.result = self.__resNone

    def get_result(self):
        if self.result is self.__resNone:
            raise RuntimeError('call get_result() before run')
        return self.result

    def run(self):
        __log__.info('[+]Thread %d starting at %s' % (self.ident, time.ctime()))
        self.result = self.cls(*self.args, **self.kwargs)()
        __log__.info('[+]Thread %d finished at %s' % (self.ident, time.ctime()))


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
        __log__.error('[-]Error: %s' % err)
    return response


class ProcedureDownloader:
    __queueEmptyTimeout = 1
    __reqFnMapping = dict()

    def __init__(self, download_dir, url_queue):
        self._urlQueue = url_queue
        self._baseDir = download_dir

    def __call__(self):
        self.make_directory()
        while True:
            if EVENT_ALL_DONE.is_set() and self._urlQueue.empty():
                break

            try:
                reqTuple = self._urlQueue.get(True, self.__queueEmptyTimeout)
                assert reqTuple[0] in self.__reqFnMapping

                __log__.debug('[+]Get: %s, Remaining count: %d' % (str(reqTuple), self._urlQueue.qsize()))

                response = download(reqTuple[1])
                if response:
                    __log__.info('[+]Download finished: %s' % reqTuple[1])
                    self.__reqFnMapping[reqTuple[0]](self, reqTuple, response)
                else:
                    __log__.error('[-]Download failed: %s' % reqTuple[1])
            except queue.Empty:
                pass
            except Exception as err:
                __log__.error('[-]Error: %s' % err)

    # req_tup: ('image', <url>, <videoIdent>)
    def _req_image(self, req_tup, response):
        if not req_tup[2]:
            filename = req_tup[1].split('/')[-1]
        else:
            filename = '%s.%s' % (req_tup[2], req_tup[1].split('.')[-1])
        self.save_file_by_response(filename, response)

    __reqFnMapping['image'] = _req_image

    # req_tup: ('page', <url>)
    def _req_page(self, req_tup, response):
        imageURLMatchObj = REGEX_SEARCH_IMAGE.search(response.text)
        if imageURLMatchObj:
            videoIdentMatchObj = REGEX_VIDEO_IDENT.search(response.url)
            videoIdent = videoIdentMatchObj.group() if videoIdentMatchObj else ''
            newReqTuple = ('image', imageURLMatchObj.group(1), videoIdent)
            self._urlQueue.put(newReqTuple)
            __log__.info('[+]Put: %s' % str(newReqTuple))
        else:
            __log__.warning('[-]Image URL not found on page %s' % req_tup[1])

    __reqFnMapping['page'] = _req_page

    def make_directory(self):
        os.makedirs(self._baseDir, exist_ok=True)

    def save_file_by_response(self, filename, response):
        filename = os.path.join(self._baseDir, filename)
        if os.path.exists(filename):
            __log__.info('[=]File has existed: %s' % filename)
        else:
            with open(filename, 'wb') as binFile:
                for chunk in response.iter_content(0xffff):
                    binFile.write(chunk)


class ProcedurePageParser:
    __instanceList = []
    __cntLock = threading.Lock()

    def __init__(self, keyword, num_pages, url_queue):
        with self.__cntLock:
            if len(self.__instanceList) >= 1:
                raise RuntimeError('not support to run larger than 1 instance of ProcedurePageParser at the same time')
            self.__instanceList.append(self)
        
        self._urlQueue = url_queue
        self._numPages = int(num_pages)
        self._keyword = str(keyword)
        self._keywordQuoted = _quote(self._keyword)

    def __call__(self):
        succeedFlag = True
        try:
            self._driver = webdriver.Chrome()
            self._driver.implicitly_wait(4)
            try:
                lastPageIndex = self.get_last_page_index()
                if lastPageIndex == -1:
                    succeedFlag = False
                else:
                    for i in range(1, min(self._numPages, lastPageIndex) + 1):
                        url = STRING_URL_BASE + _urlencode({'keyword': self._keywordQuoted, 'page': str(i)},
                                                           quote_via=_quote)
                        __log__.info('[+]Page %d downloading...' % i)
                        flag = self.collect_url_on_page(url)
                        if flag:
                            __log__.info('[+]Page %d download completed' % i)
                        else:
                            __log__.error('[-]Page %d download failed' % i)
            finally:
                self._driver.quit()
        except common.exceptions.WebDriverException as err:
            __log__.error('[-]Error: %s' % err)
        finally:
            EVENT_ALL_DONE.set()
            with self.__cntLock:
                self.__instanceList.remove(self)
        return succeedFlag

    def collect_url_on_page(self, url) -> bool:
        try:
            self._driver.get(url)
            aElems = self._driver.find_elements_by_css_selector('li[class="video matrix"]>a')
            for aElem in aElems:
                pageURL = aElem.get_attribute('href')
                reqTuple = ('page', pageURL)
                self._urlQueue.put(reqTuple)
                __log__.info('[+]Put: %s' % str(reqTuple))
            return True
        except Exception as err:
            __log__.error('[-]Error: %s, %s' % (type(err), err))
        return False

    def get_last_page_index(self) -> int:
        # State 1:
        # [1] [2] [3] [4] [5] [6] [7] ... [xx] [xxx]
        # State 2:
        #       [1] [2] [3] [4] [5] [6] [xxx]
        # State 3:
        #              xxxxxxxxxxxxxxxxxx

        try:
            url = STRING_URL_BASE + 'keyword=%s&page=1' % self._keywordQuoted
            self._driver.get(url)

            buttonElems = self._driver.find_elements_by_class_name('pagination-btn')
            if buttonElems:  # exist the page turning button
                numbers = [int(buttonElem.text) for buttonElem in buttonElems
                           if buttonElem.text.isdigit()]
                return max(numbers)

            liElems = self._driver.find_elements_by_css_selector('li[class="video matrix"]')
            if len(liElems) > 5:  # all videos - recommend videos > 5
                return 1

        except Exception as err:
            __log__.error('[-]Error: %s, %s' % (type(err), err))
        __log__.info('[-]No result: %s' % self._keyword)
        return -1


def main():
    import argparse
    parser = argparse.ArgumentParser(description='download video covers from'
                                                 ' www.bilibili.com')
    parser.add_argument('k', type=str, help='keyword for search')
    parser.add_argument('n', type=int, help='number of pages')
    parser.add_argument('-m', '--max-workers', type=int, default=4,
                        help='the number of procedures to download page and image'
                             ' (default 4)')
    parser.add_argument('-t', '--target-dir', type=str, default='img',
                        help='target directory (default ./img)')

    args = parser.parse_args()

    if os.path.exists(args.target_dir) and not os.path.isdir(args.target_dir):
        parser.error('file exists %s' % args.target_dir)
        return 2
    if args.n < 1:
        parser.error('invalid number %d' % args.n)
        return 2

    args.max_workers = min(max(args.max_workers, 1), 20)

    table = str.maketrans({c: '_' for c in r'\/:*?"<>|'})
    args.target_dir = os.path.join(args.target_dir.translate(table),
                                   args.k.translate(table))

    ###############################################################################
    urlQueue = queue.Queue()
    subThreads = list()
    try:
        subThreads.append(MyThread(cls=ProcedurePageParser,
                                   args=(args.k, args.n, urlQueue)))
        for i in range(args.max_workers):
            subThreads.append(MyThread(cls=ProcedureDownloader,
                                       args=(args.target_dir, urlQueue)))

        for i in range(len(subThreads)):
            subThreads[i].start()

        for i in range(len(subThreads)):
            while subThreads[i].is_alive():
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        EVENT_ALL_DONE.set()
    return None


@atexit.register
def _atexit():
    __log__.info('[+]All done')


if __name__ == '__main__':
    sys.exit(main())
