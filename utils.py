from tempfile import NamedTemporaryFile
from logging import debug

def x100int(f):
    """
    Multiply by 100 and round
    :param f: float number to convert
    :return: int
    """
    if f is None:
        r = 0
    else:
        r = f * 100
    return '{0:.0f}'.format(r)


def get_temp_filename():
    f = NamedTemporaryFile()
    res = f.name
    f.close()
    return res


def append_lines(f, lines):
    """
    Append lines to file
    """
    debug('Appending lines to file')
    try:
        f.seek(-1, 2)
    except OSError:
        pass
    else:
        if f.read(1) != b'\n':
            f.write(b'\r\n')
    for line in lines:
        debug('>%s', line)
        f.write(line)
        f.write(b'\r\n')
