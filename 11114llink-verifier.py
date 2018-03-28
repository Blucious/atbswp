# coding:utf8

"""Usage:link-verifier.py <pageUrl>
Example:
    link-verifier.py https://www.python.org
"""

import re
import sys
import chardet
import requests
from urllib.parse import urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup as _Bs

try:
    __import__('lxml')
    BeautifulSoup = (lambda markup: _Bs(markup, 'lxml'))
except ImportError:
    BeautifulSoup = (lambda markup: _Bs(markup, 'html.parser'))

TIMEOUT = 6
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'
}
PATTERN_URL = re.compile(r'(?:(?:(?:https?|ftp|file):)?//)?[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')


def download(url, params=None, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT
    if 'headers' not in kwargs:
        kwargs['headers'] = HEADERS
    response = None
    try:
        response = requests.get(url, params=params, **kwargs)
    except Exception as err:
        print('[-]Error:\nurl: %s\ntype: %s\ndetails: %s' % (url, type(err), err), file=sys.stderr)
    return response


def collect_raw_link(html_text):
    soup = BeautifulSoup(html_text)
    return {tag.attrs['href'] for tag in soup.select('a') if tag.attrs['href']}


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        return None

    page_response = download(sys.argv[1])
    if page_response is None:
        return 2

    encoding = chardet.detect(page_response.content)['encoding']
    if encoding is None:
        print('Non-text file')
        return 2
    page_response.encoding = encoding
    html_text = page_response.text

    url_list = []
    parse_result_parent = urlparse(sys.argv[1])
    for url in collect_raw_link(html_text):
        if PATTERN_URL.match(url):
            parse_result = urlparse(url)

            if any(parse_result):
                if not parse_result.netloc:  # relative path
                    treated_url = urlunparse(parse_result_parent[:2] + parse_result[2:])
                elif not parse_result.scheme:  # absolute path no scheme
                    treated_url = urlunparse(parse_result_parent[:1] + parse_result[1:])
                else:  # absolute path
                    treated_url = url

                print('[?]Filter: [+]%s' % url)
                if treated_url != url:
                    print('            ->%s' % treated_url)

                url_list.append(treated_url)
                continue
        print('[?]Filter: [-]%s' % url)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download, url) for url in url_list]

        for future in as_completed(futures):
            response = future.result()
            if response is not None:
                print('[+]%s - Status Code:%s' % (response.url, response.status_code))
    return None


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
