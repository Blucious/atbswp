# coding:utf8

"""Opens several * search result.
Usage:luck.py arg1[, arg1 [, arg1 [, ...]]
"""

__version__ = 1.0

import sys
import bs4, webbrowser
import urllib.parse, urllib.request


if len(sys.argv) != 1:
    print('Quoting...')
    url = 'http://www.baidu.com/s?wd=' \
          + urllib.parse.quote(' '.join(sys.argv[1:]))
    print('\'%s\'\n' % url)

    print('Searching...')
    try:
        httpResponseObj = urllib.request.urlopen(url)
    except Exception as err:
        print('Failure: ', str(err))
        sys.exit()

    htmlText = httpResponseObj.read().decode('utf8')

    bsObj = bs4.BeautifulSoup(htmlText, 'lxml')
    tagObjList = bsObj.select('div > h3 > a')

    numOpen = min(5, len(tagObjList))
    for index in range(numOpen):
        link = tagObjList[index].get('href')
        print('Opening... \'%s\'' % link)
        webbrowser.open(link)
else:
    print(__doc__)




