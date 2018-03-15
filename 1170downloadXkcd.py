# coding:utf8

# downloadXkcd.py - Downloads every single XKCD comic

import os
import bs4
import requests


url = 'http://xkcd.com'             # starting url
os.makedirs('xkcd', exist_ok=True)  # store comics in ./xkcd
while not url.endswith('#'):
    # -------------------- Download the page --------------------
    print("Downloading page %s..." % url)
    try:
        resObj = requests.get(url, timeout=35)
    except Exception as err:
        print('Failure: %s' % str(err))
        break
    if resObj.status_code != requests.codes.ok:
        print('Failure with status code: %d' % resObj.status_code)
        break

    # -------------------- Find the URL of the comic image --------------------
    bsObj = bs4.BeautifulSoup(resObj.text, 'lxml')
    tagObjList = bsObj.select('#comic img')
    if not tagObjList:
        print("Could not find comic image.")
    else:
        imageURL = 'http:' + tagObjList[0].get('src')

        # --------------- Download the image ---------------
        print("Downloading image %s..." % imageURL)
        resObj_imgbin = requests.get(imageURL)
        if resObj_imgbin.status_code != requests.codes.ok:
            print('Failure with status code: %d' % resObj_imgbin.status_code)
            break

        # --------------- Save the image to './xkcd' ---------------
        fileName = os.path.join('xkcd', os.path.basename(imageURL))
        with open(fileName, 'wb') as imgFile:
            for chunk in resObj_imgbin.iter_content(100000):
                imgFile.write(chunk)
        print("Image '%s' save finished." % fileName)

    # -------------------- Get the Prev button's url --------------------
    tagObjList = bsObj.select('li a[rel=prev]')
    if not tagObjList:
        break
    aElem = tagObjList[0]
    url = 'http://xkcd.com' + aElem.get('href')

print('Done.')


