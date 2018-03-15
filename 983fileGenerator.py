# coding:utf8

import os
import sys
import shutil
import random

import hashlib

root = './test'

if os.path.exists(root):
    sys.exit()
else:
    os.mkdir(root)

    for i in range(15):
        number = random.randint(1, 500)
        filePath = os.join(root, 'spam' + ('%03d' % number) + '.txt')
        open(filePath, 'w').close()
