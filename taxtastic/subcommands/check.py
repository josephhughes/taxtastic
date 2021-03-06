"""
Run a series of deeper checks on a RefPkg.
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
import os.path

import taxtastic.refpkg

def build_parser(parser):
    parser.add_argument('refpkg', action='store', metavar='REFPKG',
        help='Path to Refpkg to check')

def action(args):
    if not os.path.isdir(args.refpkg):
        print args.refpkg, 'is not a directory.'
        return 1

    r = taxtastic.refpkg.Refpkg(args.refpkg)
    msg = r.is_ill_formed()
    if msg:
        print msg
        return 1
    else:
        return 0
