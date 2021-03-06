from datetime import timedelta, datetime, time
import psycopg2
import psycopg2.extras
from utils import x100int
from settings import DB_HOST, DB_PORT, DATABASE, USERNAME, PASSWORD
import logging


ONE_DAY = timedelta(days=1)


class Exporter(object):
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, database=DATABASE, user=USERNAME,
            password=PASSWORD)

    def get_routes(self, d):
        """
        Get routes for specified date

        :param d: Date for which we will export route data
        """
        zdate = datetime.combine(d.date(), time())
        start_date = zdate - ONE_DAY + timedelta(hours=20)
        end_date = zdate + ONE_DAY
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
            c.execute(
                'SELECT * FROM asiomm_export '  # ...
                'WHERE (dt_begin >= %s) AND (dt_begin < %s)',
                (start_date, end_date))
            for rec in c:
                yield rec

    def close_connection(self):
        self.conn.close()


def record_to_csv(rec):
    d = datetime.now()
    sectiod_id = rec['id_sectionoflocomotive']
    section_index = '"{0:02d}"'.format(sectiod_id % 10)
    section_number = '"{0:08d}"'.format((sectiod_id // 10) % 100000)
    series_code = '"{0:03d}"'.format(sectiod_id // 1000000)
    dt_begin = '"%s"' % (rec['dt_begin'].strftime('%Y-%m-%d-%H.%M.%S.000000'))
    dt_end = '"%s"' % (rec['dt_end'].strftime('%Y-%m-%d-%H.%M.%S.000000'), )
    d_strftime = d.strftime('"%Y-%m-%d-%H.%M.%S.000000"')
    line = ','.join((
        d.strftime('%Y%m%d'),
        '"{}"'.format(rec['numberrouter'].strip()),
        '"{}"'.format(str(rec['asiomm_id'])),
        '"{}"'.format(rec['fullname']),
        series_code, section_number, section_index,
        dt_begin, dt_end, '9',
        x100int(rec['pokazlastd']),
        x100int(rec['firstpokaz']),
        x100int(rec['lastpokaz']),
        '0',
        x100int(rec['firstpokazrecup']),
        x100int(rec['firstpokazrecup']),
        x100int(rec['lastpokazrecup']),
        '0',
        x100int(rec['firstheatingpokaz']),
        x100int(rec['firstheatingpokaz']),
        x100int(rec['lastheatingpokaz']),
        '0', '0', '0',
        d_strftime,
        d_strftime,
        d_strftime)).encode('cp1251', errors='replace')
    return line
