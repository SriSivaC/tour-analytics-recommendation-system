import hashlib
from struct import pack
from binascii import hexlify
# from frontera.utils.url import parse_url
from zlib import crc32
from six.moves.urllib import parse
from w3lib.util import to_bytes, to_native_str


def parse_url(url, encoding=None):
    """Return urlparsed url from the given argument (which could be an already
    parsed url)
    """
    return url if isinstance(url, parse.ParseResult) else \
        parse.urlparse(to_native_str(url))


def to_signed32(x):
    """ If x is an usigned 32-bit int, convert it to a signed 32-bit.
    """
    return x - 0x100000000 if x > 0x7fffffff else x


def get_crc32(name):
    """ signed crc32 of bytes or unicode.
    In python 3, return the same number as in python 2, converting to
    [-2**31, 2**31-1] range. This is done to maintain backwards compatibility
    with python 2, since checksums are stored in the database, so this allows
    to keep the same database schema.
    """
    return to_signed32(crc32(to_bytes(name, 'utf-8', 'ignore')))


def sha1(key):
    return to_bytes(hashlib.sha1(to_bytes(key, 'utf8')).hexdigest())


def md5(key):
    return to_bytes(hashlib.md5(to_bytes(key, 'utf8')).hexdigest())


def hostname_local_fingerprint(key):
    """
    This function is used for URL fingerprinting, which serves to uniquely identify the document in storage.
    ``hostname_local_fingerprint`` is constructing fingerprint getting first 4 bytes as Crc32 from host, and rest is MD5
    from rest of the URL. Default option is set to make use of HBase block cache. It is expected to fit all the documents
    of average website within one cache block, which can be efficiently read from disk once.
    :param key: str URL
    :return: str 20 bytes hex string
    """
    result = parse_url(key)
    hostname = result.hostname if result.hostname else '-'
    host_checksum = get_crc32(hostname)
    combined = hostname+result.path+';'+result.params+result.query+result.fragment

    combined = to_bytes(combined, 'utf8', 'ignore')
    doc_fprint = hashlib.md5(combined).digest()
    fprint = hexlify(pack(">i16s", host_checksum, doc_fprint))
    return fprint
