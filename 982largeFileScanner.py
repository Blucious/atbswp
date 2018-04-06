# coding:utf8

"""Usage:largeFileFind.py <dir> <size>
Example:
    largeFileFind.py ./spam 0.1g
    largeFileFind.py ./spam 100MB
    largeFileFind.py ./spam 100Mb  # different to 100MB
    largeFileFind.py ./spam 100kk  # equal to 100MB
"""

import re
import os
import sys

REGEX_SIZE = re.compile(r'^(\d+(?:\.\d+)?)([A-Za-z]{1,2})$')

# Unit base on bytes.
UNIT_b = 0.125
UNIT_B = 1
UNIT_K = UNIT_B * 1024
UNIT_M = UNIT_K * 1024
UNIT_G = UNIT_M * 1024
UNIT_T = UNIT_G * 1024

UNIT2BYTES = {'T': UNIT_T, 't': UNIT_T,
              'G': UNIT_G, 'g': UNIT_G,
              'M': UNIT_M, 'm': UNIT_M,
              'K': UNIT_K, 'k': UNIT_K,
              'B': UNIT_B,
              'b': UNIT_b}


def formatString2nBytes(fmtString):
    matchObject = REGEX_SIZE.match(fmtString)
    if not matchObject:
        return None

    digitPart = matchObject.group(1)
    unitPart = matchObject.group(2)

    nBytes = float(digitPart)
    for unit in unitPart:
        if unit not in UNIT2BYTES:
            return None
        else:
            nBytes *= UNIT2BYTES[unit]

    return round(nBytes)


def nBytes2formatString(nBytes, precision=3):
    stepToGreaterUnit = 1024.

    nBytes = float(nBytes)
    unit = 'bytes'

    if (nBytes / stepToGreaterUnit) >= 1:
        nBytes /= stepToGreaterUnit
        unit = 'KB'

    if (nBytes / stepToGreaterUnit) >= 1:
        nBytes /= stepToGreaterUnit
        unit = 'MB'

    if (nBytes / stepToGreaterUnit) >= 1:
        nBytes /= stepToGreaterUnit
        unit = 'GB'

    if (nBytes / stepToGreaterUnit) >= 1:
        nBytes /= stepToGreaterUnit
        unit = 'TB'

    nBytes = round(nBytes, precision)

    return str(nBytes) + unit


if len(sys.argv) == 3:
    if not os.path.exists(sys.argv[1]):
        sys.exit()
    minimum = formatString2nBytes(sys.argv[2])
    if minimum is None:
        print('Invalid format')
        sys.exit()

    for root, dirs, files in os.walk(sys.argv[1]):
        foundFlag = False
        for file in files:
            try:
                fileAbsPath = os.path.join(root, file)
                fileSize = os.path.getsize(fileAbsPath)
                if fileSize >= minimum:
                    if not foundFlag:
                        foundFlag = True
                        print("Directory '%s'" % root)
                    print("\t'%s' - %s" % (fileAbsPath, nBytes2formatString(fileSize)))
            except FileNotFoundError:
                pass
        if foundFlag:
            print()
else:
    print(__doc__)
