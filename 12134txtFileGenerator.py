# coding:utf8

import os
import random

BASE_DIR = os.path.curdir + os.path.sep + '12134testFile'

try:
    os.mkdir(BASE_DIR)
except FileExistsError:
    pass

for i in range(1, 11):
    with open(os.path.join(BASE_DIR, '%d.txt' % i), 'w') as f:
        for j in range(random.randint(1, 11)):
            f.write('%d\n' % random.randint(1, 10000))
