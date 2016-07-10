import os
import re
import io
'''
from os.path import dirname, isdir
from urllib.request import urlretrieve
from zipfile import ZipFile

import requests
import sys
'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(*names, **kwargs):
    with io.open(
            os.path.join(os.path.dirname(__file__), *names),
            encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


NAME = "drunkbot"
META_PATH = os.path.join("drunk_bot", "__init__.py")
KEYWORDS = ["drunkbot", "discord", "bot", "audio scraper", "video scraper", "youtube"]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "License :: Other/Proprietary License",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
INSTALL_REQUIRES = ["six", "soundscrape", "pafy", "youtube-dl", "youtube-dl-plugin", "pynacl", "discord.py",
                    "ImageScraper", "beautifulsoup4", "bs4", "chatterbot", "cleverbot", "cython", "numpy", "clint",
                    "websockets", "sqlalchemy", "soundcloud", "simplejson", "pyvirtualdisplay", "nltk", "lxml",
                    "chardet", "cffi", "aiohttp", "SimplePool", "splinter", "selenium"]
HERE = os.path.abspath(os.path.dirname(__file__))
META_FILE = read(*[META_PATH])


def find_meta(meta):
    global META_FILE
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("uri"),
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        keywords=KEYWORDS,
        long_description=read(*["README.md"]),
        packages=["drunk_bot"],
        classifiers=CLASSIFIERS,
        scripts=["drunkbot"],
        install_requires=INSTALL_REQUIRES,
    )

    '''
    try:
        from drunk_bot import Sync
    except ImportError:
        print("\n" * 5)
        raise OSError("Failed installing!!! couldn't find the package...")

    package_path = dirname(Sync.__file__) + "/"

    _file = "src.zip"
    link = "http://download1252.mediafire.com/5w2d9oa7l5sg/5xd1bybx7b0dfbx/src.zip"

    """
    Snippet pulled from: http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
    """


    def reporthook(blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            s = "\r%5.1f%% %*d / %d" % (
                percent, len(str(totalsize)), readsofar, totalsize)
            sys.stderr.write(s)
            if readsofar >= totalsize:  # near the end
                sys.stderr.write("\n")
        else:  # total size is unknown
            sys.stderr.write("read %d\n" % (readsofar,))


    print("Downloading ffmpeg binaries")
    urlretrieve(link, _file, reporthook)

    zips = ZipFile(_file, 'r')
    zips.extractall(package_path)
    zips.close()
    '''

    print("Done installing drunkbot now please auth the bot like such\n\ndrunkbot --token TOKENID")
