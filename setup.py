# run from the command line using:
# python setup.py py2exe
#
# python pyinstaller.py -F --noconsole D:/Coding/GitHub/pad-helper/pad-helper.py

"""
from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    windows = [{'script': "pad-helper.py"}],
    zipfile = None,
)
"""