"""Extracts tax ids of all lonely nodes in a taxtable."""
# This file is part of taxtastic.
#
#    taxtastic is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    taxtastic is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with taxtastic.  If not, see <http://www.gnu.org/licenses/>.

import logging
import shutil
import os
import time
import shutil
import hashlib
import re
import json
import sys

from taxtastic import lonely, refpkg

log = logging.getLogger(__name__)

class ConfigError(Exception):
    pass

def build_parser(parser):
    parser.add_argument("target",
                        metavar = "taxtable_or_refpkg", 
                        action="store",
                        help='A taxtable or a refpkg containing a taxtable')
    parser.add_argument('-o', '--output',
                        action='store', default=None,
                        help='Write output to given file')
    parser.add_argument('-v', '--verbose',
                        action="store_true", dest="verbose", default = False,
                        help= 'Print details')


def action(args):
    if not(os.path.exists(args.target)):
        print >>sys.stderr, "Failed: no such target %s" % args.target
        return 1
    elif os.path.isdir(args.target):
        try:
            if args.verbose:
                print >>sys.stderr, "Target is a refpkg. Working on taxonomy within it."
            r = refpkg.Refpkg(args.target)
            path = r.file_abspath('taxonomy')
        except e:
            print >>sys.stderr, "Failed: %s" % str(e)
            return 1
    else:
        if args.verbose:
            print >>sys.stderr, "Target is a CSV file."
        path = args.target
        
    print >>sys.stderr, "Loading taxonomy from file...",
    with open(path) as h:
        tree = lonely.taxtable_to_tree(h)
    print >>sys.stderr, "done."
    txt = '\n'.join(["%s # %s %s" % (n.key if n.key else "", n.rank, n.tax_name) for n in tree.lonelynodes()])
    if args.output:
        with open(args.output, 'w') as out:
            print >>out, txt
    else:
        print txt
    return 0
