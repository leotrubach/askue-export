DB_HOST = '127.0.0.1'
DB_PORT = 5555

try:
    from local_settings import *
except ImportError:
    pass