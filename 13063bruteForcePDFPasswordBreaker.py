# coding:utf8

"""bruteForcePDFPasswordBreaker.py -h PDF DICT [DICT ... [DICT [DICT]]]
"""

import os
import sys
import time
import PyPDF2


class DecryptionDone(Exception): pass
class UnencryptedFileError(Exception): pass


def main(pdf, dictionaries):
    if not os.path.isfile(pdf) or not pdf.endswith('.pdf'):
        print('Invalid file or file name {}')
        return 1

    for dictionary in dictionaries:
        if not os.path.isfile(dictionary):
            print('Invalid file or file name {}'.format(dictionary))
            return 1

    print('Dictionary(ies): {}'.format(str(dictionaries)[1:-1]))
    print("PDF: '{}'".format(pdf))
    print()
    print('Start from {}'.format(time.ctime()))
    print()

    password = None
    count = 0
    try:
        with open(pdf, 'rb') as pdfFile:
            pdfReader = PyPDF2.PdfFileReader(pdfFile)
            if not pdfReader.isEncrypted:
                raise UnencryptedFileError()

            for dictionary in dictionaries:
                with open(dictionary, 'r') as dictFile:
                    for key in dictFile:
                        key = key.strip('\n')

                        for password in [key, key.lower()]:
                            count += 1
                            if pdfReader.decrypt(password) > 0:
                                raise DecryptionDone()

                        if count % 50 == 0:
                            print('\033[1ACount: {0:<7}'.format(count))
    except UnencryptedFileError:
        print("{1:#<8} Unencrypted file '{0}' {1:#<8}".format(pdf, ''))
    except DecryptionDone:
        print("{1:#<8} Password found '{0}' {1:#<8}".format(password, ''))
    else:
        print('{0:#<8} failure {0:#<8}'.format(''))
    print('Done at {}'.format(time.ctime()))
    return None


if len(sys.argv) >= 3:
    sys.exit(main(sys.argv[1], sys.argv[2:]))
else:
    print(__doc__)
    if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help'):
        sys.exit(0)
    sys.exit(1)

