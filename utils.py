from tempfile import NamedTemporaryFile
from logging import debug

def x100int(f):
    """
    Multiply by 100 and round
    :param f: float number to convert
    :return: int
    """
    return '{0:.0f}'.format(f * 100)


def get_temp_filename():
    f = NamedTemporaryFile()
    res = f.name
    f.close()
    return res


def append_lines(f, lines):
    """
    Append lines to file
    """
    f.seek(-1, 2)
    if f.read(1) != b'\n':
        f.write(b'\r\n')
    for line in lines:
        debug('>%s', line)
        f.write(line)
        f.write(b'\r\n')
