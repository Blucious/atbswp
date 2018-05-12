# coding:utf8

"""Usage: pdfParanoia.py PASSWORD
Example:
    pdfParanoia.py eggs
"""

import os
import sys
import send2trash
import PyPDF2

SUFFIX = '_encrypted.pdf'


def test(filename, password, raise_for_invalid_file=True) -> bool:
    if not os.path.isfile(filename):
        if raise_for_invalid_file:
            raise RuntimeError('invalid file or filename {}'.format(filename))
        else:
            return False

    with open(filename, 'rb') as pdf_rf:
        reader = PyPDF2.PdfFileReader(pdf_rf)
        status_code = reader.decrypt(password)
    return status_code == 1


def encrypt(filename1, filename2, password):
    with open(filename1, 'rb') as pdf_rf:
        reader = PyPDF2.PdfFileReader(pdf_rf)
        if reader.isEncrypted:
            print('[-]', 'File has been encrypted: {}'.format(filename1))
            return False

        # Copy
        writer = PyPDF2.PdfFileWriter()
        writer.appendPagesFromReader(reader)

        # Encrypt
        writer.encrypt(password)

        # Wirte out
        with open(filename2, 'wb') as pdf_wf:
            writer.write(pdf_wf)

        print('[+]', filename1, '->', filename2)
    return True


def main(password):
    for root, dirs, filenames in os.walk('.'):
        for filename in filenames:
            filename = os.path.join(root, filename)
            filename_exclude_extension, extension = os.path.splitext(filename)
            if extension != '.pdf' or filename.endswith(SUFFIX):
                if filename.endswith(SUFFIX):
                    print('[=] Ignore: {}'.format(filename))
                continue

            new_filename = filename_exclude_extension + SUFFIX
            if not encrypt(filename, new_filename, password):
                continue

            # Delete
            send2trash.send2trash(filename)
            print('[+] Remove: {}'.format(filename))
    return None


if len(sys.argv) == 2 and sys.argv[1] not in ('-h', '--help'):
    sys.exit(main(sys.argv[1]))
else:
    print(__doc__)
    if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help'):
        sys.exit(1)
    sys.exit(0)

