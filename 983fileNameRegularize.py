# coding:utf8

"""Usage:fileNameRegularize.py <dir> <prefix> [<startIndex>]
Example:
    fileNameRegularize.py ./spam spam       # Use the minimum index that exists
    fileNameRegularize.py ./spam spam 001   # Use placeholder
    fileNameRegularize.py ./spam spam 1     # '1' is different to '001'
"""

import re
import os
import sys
import collections

prefixPatternTemplate = r'^(%s)((0*?)\d+)(.*)$'

GROUP_PREFIX = 1
GROUP_DECIMAL = 2
GROUP_LEADING_ZERO = 3
GROUP_TAILING = 4


def get_matched_files(pattern, dir_path):
    sequence = filter(None, [pattern.match(f) for f in os.listdir(dir_path)])
    if not sequence:
        return None
    sequence = list(sorted(sequence,
                           key=lambda m: int(m.group(GROUP_DECIMAL))))
    # -> [mo1, mo2, ...]
    return sequence


def omit_path(path):
    if path.count(os.sep) > 5:
        parts = path.split(os.sep)
        return os.sep.join(parts[:2] + ['...'] + parts[-2:])
    else:
        return path


if len(sys.argv) in (3, 4):
    # --------------- Directory ---------------
    if not os.path.exists(sys.argv[1]):
        sys.exit()
    else:
        dirPath = os.path.abspath(sys.argv[1])
    # --------------- Prefix ---------------
    try:
        prefixPattern = re.compile(prefixPatternTemplate % sys.argv[2])
    except re.error as err:
        print('ERROR: %s' % str(err))
        sys.exit()
    else:
        matchObjects = get_matched_files(prefixPattern, sys.argv[1])
        if not matchObjects:
            print('Specified file not found')
            sys.exit()
    # --------------- Start index ---------------
    if len(sys.argv) == 4:
        try:
            startIndex = int(sys.argv[3])
        except ValueError as err:
            print('ERROR: %s' % str(err))
            sys.exit()
    else:
        startIndex = int(matchObjects[0].group(GROUP_DECIMAL))

    # --------------- Leading zero ---------------
    if len(sys.argv) == 4 and sys.argv[3].startswith('0') and len(sys.argv[3]) != 1 \
            or matchObjects[0].group(GROUP_LEADING_ZERO):
        numPlaceholder = 0
        if len(sys.argv) == 4:
            numPlaceholder = len(sys.argv[3])
        else:
            numPlaceholder = len(matchObjects[0].group(GROUP_DECIMAL))
        indexTemplate = '%%0%dd' % numPlaceholder
    else:
        indexTemplate = '%d'

    # --------------- Loop ---------------
    print('Start at', startIndex)
    iterSequence = list(enumerate(matchObjects, startIndex))
    for index, matchObject in iterSequence:
        if (indexTemplate % index) != matchObject.group(GROUP_DECIMAL):
            filename = matchObject.group()

            src = os.path.join(dirPath, filename)
            dst = os.path.join(dirPath,
                               matchObject.group(GROUP_PREFIX)
                               + (indexTemplate % index)
                               + matchObject.group(GROUP_TAILING))

            # The name to be modified is the name to be modified next.
            if os.path.exists(dst):
                # Append to the end of sequence, otherwise it will raise FileExistsError
                iterSequence.append((index, matchObject))
                continue

            print("Renaming... '%s' -> '%s'" % (omit_path(src), omit_path(dst)))
            os.rename(src, dst)
        else:
            print("File exists '%s'" % matchObject.group())
else:
    print(__doc__)
