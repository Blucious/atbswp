# coding:utf8

"""Usage:link-verifier.py <pageUrl>
Example:
    link-verifier.py https://www.python.org
"""

import re
import sys
import chardet
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 12
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'
}
# PATTERN_LINK = re.compile(r'"((?:(?:https|http):)?//[^"]+)"')
# PATTERN_LINK = re.compile(r'//[-A-Za-z0-9+&@#/%?=~|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
PATTERN_LINK = re.compile(r'(?:"|\'|=)((?:https?:)?//[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])')


def download(url, params=None, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT
    if 'headers' not in kwargs:
        kwargs['headers'] = HEADERS
    response = None
    try:
        response = requests.get(url, params=params, **kwargs)
    except Exception as err:
        print('[-]Error:\nurl: %s\ntype: %s\ndetails: %s' % (url, type(err), err),
              file=sys.stderr)
    return response


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    pageReponse = download(sys.argv[1])
    if pageReponse is None:
        return 2

    encoding = chardet.detect(pageReponse.content)['encoding']
    if encoding is None:
        print('Non-text file')
        return 2
    pageReponse.encoding = encoding
    text = pageReponse.text

    protocol = urlparse(sys.argv[1]).scheme
    urlSet = set(PATTERN_LINK.findall(text))
    urlList = []
    for url in urlSet:
        SextupleTuple = urlparse(url)
        if not SextupleTuple.path or SextupleTuple.path.endswith('/') or '.' not in SextupleTuple.path or \
                SextupleTuple.path.split('.')[-1] in ('htm', 'html', 'asp', 'jsp', 'php'):
            urlList.append(url if urlparse(url).scheme else '%s:%s' % (protocol, url))
            print('[?]Filter: [+]%s' % url)
        else:
            print('[?]Filter: [-]%s' % url)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futureList = [executor.submit(download, url) for url in urlList]
        for future in as_completed(futureList):
            response = future.result()
            if response is not None:
                print('[+]%s - Status Code:%s' % (response.url, response.status_code))
    return None


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
