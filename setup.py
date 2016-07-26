#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    setup.py
    ~~~~~~~~

    no description available

    :copyright: (c) 2016 by scribe.
    :license: see LICENSE for more details.
"""

import codecs
import os
import re
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Taken from pypa pip setup.py:
    intentionally *not* adding an encoding option to open, See:
       https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    """
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def requirements():
    """Returns requirements.txt as a list usable by setuptools"""
    import os
    reqtxt = os.path.join(_path, u'requirements.txt')
    with open(reqtxt) as f:
        return f.read().split()

setup(
    name='iabooks',
    version=find_version("iabooks", "__init__.py"),
    description="Full-text search Archive.org's library of Greek & Roman classics",
    long_description=read('README.rst'),
    classifiers=[
        ],
    author='Archive Labs',
    author_email='mek@archive.org',
    url='https://books.archivelab.org',
    packages=[
        'iabooks'
        ],
    platforms='any',
    license='AGPL-3',
    install_requires=requirements()
)
