# coding:utf8

# bubbetPointAdder.py - Adds Wikipedia bullet points to the start
# of each line of text on the clipboard

import pyperclip

text = pyperclip.paste()

# Separate lines and add stars
lines = text.split('\n')
for index in range(len(lines)):
    lines[index] = '* ' + lines[index]
text = ''.join(lines)
pyperclip.copy(text)


