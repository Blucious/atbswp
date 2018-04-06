# coding:utf8

"""Usage:txtToSpreadsheet.py <fileName>"""

import os
import sys
import glob
import openpyxl

FUNC_FILTER = (lambda _fn: os.path.isfile(_fn) and _fn.endswith('.txt'))


if len(sys.argv) > 1:
    if len(sys.argv) == 2:
        fn_list = list(filter(FUNC_FILTER, glob.glob(sys.argv[1])))
    else:
        fn_list = list(filter(FUNC_FILTER, sys.argv[1:]))

    if not fn_list:
        print('[-]No match')
        sys.exit()
    import pprint
    print('[+]Match list: %s' % pprint.pformat(fn_list))

    try:
        wb = openpyxl.Workbook()
    except PermissionError as err:
        print('[-]Error: %s' % str(err))
        sys.exit()

    try:
        ws = wb.active
        try:
            fn_list.sort(key=lambda _fn: int(
                os.path.splitext(os.path.basename(_fn))[0]))
        except TypeError:
            pass

        for i, fn in enumerate(fn_list, 1):
            with open(fn) as fio:
                for j, line in enumerate(fio, 1):
                    ws.cell(j, i).value = line.strip()
        wb.save('12134.xlsx')
    except PermissionError as err:
        print('[-]Error: %s' % str(err))
    finally:
        wb.close()

    print('[+]Done')
else:
    print(__doc__)
