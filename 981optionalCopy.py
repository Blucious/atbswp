# coding:utf8

"""Usage:optionalCopy.py [dir] [extensions] [destdir]
example:
    optionalCopy.py ./eggs jpg,pdf ./bacon
    optionalCopy.py ./eggs .jpg,.pdf ./bacon
"""

import os
import sys
import shutil

if len(sys.argv) == 4:
    # sys.argv[1] directory
    # sys.argv[2] file extensions
    # sys.argv[3] destination directory

    if not os.path.exists(sys.argv[1]):
        print('Directory not found')
        sys.exit()
    try:
        if not os.path.exists(sys.argv[3]):
            print("Creating '%s'..." % sys.argv[3])
            os.mkdir(sys.argv[3])
    except (PermissionError, OSError) as err:
        print('ERROR: %s' % str(err))
        sys.exit()
    fileExtensions = [ext if ext.startswith('.') else '.' + ext
                      for ext in sys.argv[2].split(',') if ext]
    if not fileExtensions:
        sys.exit()

    # Walk the entire directory.
    for root, dirs, files in os.walk(sys.argv[1]):
        for file in files:
            if os.path.splitext(file)[1] in fileExtensions:
                src = os.path.join(root, file)
                dst = os.path.join(sys.argv[3], file)
                print("Copying '%s'..." % src)
                shutil.copy(src, dst)
else:
    print(__doc__)

