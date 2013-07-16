from datetime import datetime
from exporter import Exporter, record_to_csv
from ftplib import FTP
import logging
import logging.handlers
from tempfile import NamedTemporaryFile
import os
from os.path import join as j, exists, dirname
import re
import time

import settings as S
from utils import append_lines

if not exists(S.LOG_DIR):
    os.mkdir(S.LOG_DIR)
LOGGING_FORMAT = '%(levelname)s:%(filename)s:%(asctime)s:%(message)s'
logging.basicConfig(format=LOGGING_FORMAT)
rl = logging.getLogger()
rl.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOGGING_FORMAT)
fh = logging.handlers.RotatingFileHandler(
    S.LOG_FILE, maxBytes=1000000, backupCount=10)
fh.setFormatter(formatter)
rl.addHandler(fh)


ASKUE_FNAME_REGEXP = re.compile('^\d{8}askct_to_iomm\.txt$')

def askue_filename(s):
    return ASKUE_FNAME_REGEXP.match(s.lower())


def date_from_filename(s):
    try:
        return datetime.strptime(s[:8], '%d%m%Y')
    except ValueError:
        return datetime(1970, 1, 1)


def process_askue():
    e = Exporter()
    try:
        with FTP(S.FTP_SERVER, S.FTP_USER, S.FTP_PASSWORD) as fc:
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
            ftp_pos = tf.tell()
            try:
                if S.APPEND_ON:
                    lines = (record_to_csv(rec) for rec in e.get_routes(datetime.now()))
                    append_lines(tf, lines)
            except Exception:
                tf.seek(ftp_pos)
                tf.truncate()
            tf.seek(0)
            dest_path = j(S.IOMM_PATH, rfile)
            # Send file back to FTP
            logging.info('Sending file... {}'.format(dest_path))
            fc.storbinary('STOR {}'.format(dest_path), tf)
            logging.info('Cleaning up directory...')
            for fname in filenames:
                filepath = j(S.REMS_PATH, fname)
                fc.delete(filepath)
    finally:
        e.close_connection()


def main():
    while True:
        try:
            process_askue()
            time.sleep(S.RETRY_INTERVAL)
        except Exception:
            logging.exception('Got exception:')
            pass


if __name__ == '__main__':
    main()