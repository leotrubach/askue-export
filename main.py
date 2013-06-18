from datetime import datetime
from exporter import Exporter, record_to_csv
from ftplib import FTP
import logging
from tempfile import NamedTemporaryFile
from os.path import join as j
import re
import time

import settings as S
from utils import append_lines

ASKUE_FNAME_REGEXP = re.compile('^\d{8}askct_to_iomm\.txt$')

def askue_filename(s):
    return ASKUE_FNAME_REGEXP.match(s.lower())


def date_from_filename(s):
    try:
        datetime.strptime(s[:8], '%d%m%Y')
    except ValueError:
        return datetime(1970, 1, 1)


def process_askue():
    e = Exporter()
    with FTP(S.DB_HOST, S.FTP_USER, S.FTP_PASSWORD) as fc:
        # Find files and retrieve it
        inbox_files = fc.mlsd(S.REMS_PATH)
        filenames = [e[0] for e in inbox_files if askue_filename(e[0])]
        if not filenames:
            logging.info('Inbox directory is empty...')
            return
        if len(filenames) > 1:
            logging.debug('More than 1 file were found: {}'.format('\n'.join(filenames)))
        rfile = max(filenames, key=date_from_filename)
        logging.info('Retrieving {}...'.format(rfile))
        tf = NamedTemporaryFile()
        fc.retrbinary('RETR {}'.format(j(S.REMS_PATH, rfile)), tf.write)
        # Append data to file
        lines = (record_to_csv(rec) for rec in e.get_routes(datetime.now()))
        append_lines(tf, lines)
        tf.seek(0)
        dest_path = j(S.IOMM_PATH, rfile)
        # Send file back to FTP
        logging.info('Sending file... {}'.format(dest_path))
        fc.storbinary('STOR {}'.format(dest_path), tf)
        logging.info('Cleaning up directory...')
        for fname in filenames:
            filepath = j(S.REMS_PATH, fname)
            fc.delete(filepath)


def main():
    process_askue()
    time.sleep(60000)


if __name__ == '__main__':
    main()