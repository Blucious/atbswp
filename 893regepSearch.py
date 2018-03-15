# coding:utf8
"""usage:regepSearch893.py [targetdir] [regexp]
example:
    regepSearch893.py ./ "\d{4}-\d{2}-\d{2}"
"""

import re
import sys, os

if len(sys.argv) == 3:
    if not os.path.isdir(sys.argv[1]):
        sys.exit()
    try:
        searchRegex = re.compile(sys.argv[2])
    except re.error as err:
        print("COMPILE ERROR:", err)
        print(__doc__)
        sys.exit()

    fileNameList = []
    for fileName in [s for s in os.listdir(sys.argv[1]) if s.endswith(".txt")]:
        print('File "%s"' % fileName)
        with open(fileName, encoding="utf8") as textFile:
            lineno = 0
            while True:
                line = textFile.readline()
                lineno += 1
                if not line:
                    break

                resultsList = searchRegex.findall(line)
                if resultsList:
                    print("    Line %d - %s" % (lineno, ", ".join(resultsList)))

else:
    print(__doc__)
