# coding:utf8

# mcb.pyw - Saves and loads pieces of text to the clipboard
# Useage: py.exe mcb.pyw save <keyword> - Saves clipboard to keyword
#         py.exe mcb.pyw <keyword> - Loads keyword to clipboard
#         py.exe mcb.pyw list - Loads all keywords to clipboard

import shelve, pyperclip, sys


if len(sys.argv) in (2, 3):

    mcbShelf = shelve.open("clipdb")

    if len(sys.argv) == 3:
        if sys.argv[1].lower() == "save":
            mcbShelf[sys.argv[2]] = pyperclip.paste()
        elif sys.argv[1].lower() == "delete" and sys.argv[2] in mcbShelf:
            del mcbShelf[sys.argv[2]]
    elif len(sys.argv) == 2:
        if sys.argv[1].lower() == 'list':
            pyperclip.copy(str(list(mcbShelf.keys())))
        elif sys.argv[1].lower() == "delete":
            mcbShelf.clear()
        elif sys.argv[1] in mcbShelf:
            pyperclip.copy(mcbShelf[sys.argv[1]])

    mcbShelf.close()



