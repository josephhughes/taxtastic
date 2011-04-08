import os
import sys
import logging
import re

# set verbosity of logging output
try:
    logflag = re.findall(r'-[vq]+\b', ' '.join(sys.argv[1:]))[0]
except IndexError:
    logflag = ''

logging.basicConfig(
    file = sys.stdout,
    format = '%(levelname)s %(module)s %(lineno)s %(message)s' \
        if logflag.startswith('-v') else '%(message)s',
    level = {'-q':logging.ERROR,
             '':logging.WARNING,
             '-v': logging.INFO,
             '-vv': logging.DEBUG}[logflag]
    )

datadir = 'testfiles'
outputdir = 'test_output'

try:
    os.mkdir(outputdir)
except OSError:
    pass

