# coding:utf8

import bs4

exampleHtml = """
<!-- This is the example.html example file. -->
<html><head><title>The Website Title</title></head>
<body>
<p>Download my <strong>Python</strong> book from <a href="http://
inventwithpython.com">my website</a>.</p>
<p class="slogan">Learn Python the easy way!</p>
<p>By <span id="author">Al Sweigart</span></p>
</body></html>
"""

exampleSoup = bs4.BeautifulSoup(markup=exampleHtml, features='lxml')
print('The type of the bs4.BeautifulSoup() return value:', type(exampleSoup))

elems = exampleSoup.select('#author')
print('The type of the bs4.BeautifulSoup.select() return value:', type(elems))


print('The type of the list elements:', type(elems[0]))

print(elems[0].getText())
print(str(elems[0]))
print(elems[0].attrs)
print('-' * 80)


pElems = exampleSoup.select('p')
print(str(pElems[0]))

print(pElems[0].getText())
print('-'*55)

print(str(pElems[1]))
print(pElems[1].getText())
print('-'*55)

print(str(pElems[2]))
print(pElems[2].getText())
print('-'*80)

spanElem = exampleSoup.select('span')[0]

print(spanElem.get('id'))

print(spanElem.get('some_nonexistent_addr'))



