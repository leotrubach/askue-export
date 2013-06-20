from os.path import join as j

DB_HOST = '127.0.0.1'
DB_PORT = 5555
DATABASE = 'rems_db'
USERNAME = 'rems_admin'
PASSWORD = 'remstns'
FTP_SERVER = '91.185.1.94'
FTP_USER = 'user_asiomm'
FTP_PASSWORD = 'as948djks'
TEMP_PATH = '/REMS/TEMP'
REMS_PATH = '/REMS/'
IOMM_PATH = '/asiomm_outbox/'
LOG_DIR = 'logs'
LOG_FILE = j('logs', 'exporter.log')
RETRY_INTERVAL = 60

try:
    from local_settings import *
except ImportError:
    pass