"""
Resolve path; get the path to a file in the reference package.

Usage is simple: `taxit rp my.refpkg tree` will cause the absolute path to the
`tree` file in the refpkg to be written to stdout.
"""
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
import sys

from taxtastic import refpkg

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('refpkg', action='store', metavar='refpkg',
                        help='the reference package to operate on')
    parser.add_argument('item', action='store', metavar='item',
                        help='the item to get out of the reference package')


def action(args):
    rp = refpkg.Refpkg(args.refpkg)
    sys.stdout.write('%s\n' % rp.file_abspath(args.item))
    return 0
