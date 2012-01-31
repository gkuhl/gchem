#! /usr/bin/env python
# coding: utf-8

# Python Script Collection for GEOS-Chem Chemistry Transport Model (gchem)
# Copyright (C) 2012 Gerrit Kuhlmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""\
Miscellaneous routine(s) (gchem.misc), which currently don't fit
somewhere else.
"""

import collections
import datetime
import struct

import numpy
import uff


def iter_dates(start, end, step=1):
    """\
    Iterate over datetime objects from `start` till `end` with `step`
    (default 1) days.

    Example:
    >>> from datetime import datetime
    >>> for date in iter_dates(datetime(2011,1,1), datetime(2011,2,1)):
            print date
    """
    current = start
    while current < end:
        yield current
        current += datetime.timedelta(days=1)


def tau2time(tau, reference=datetime.datetime(1985,1,1)):
    """ hours since reference (01.01.1985 00:00) -> datetime object """
    return reference + datetime.timedelta(hours=tau)


def time2tau(time, reference=datetime.datetime(1985,1,1)):
    """ datetime object -> hours since reference (01.01.1985 00:00) """
    return (time - reference).total_seconds() / 3600.0


def read_gmao(filename, endian='>', skip_rows=1):
    """\
    read(filename, endian='>', skip_rows=1)

    Read GMAO met fields from `filename`. Data are returned as nested
    dictionary with: field_name -> timestamp -> data.
    """
    SIZE2SHAPE = {
        943488: (144,91,72),
        956592: (144,91,73),
        13104:  (144,91)
    }

    data = collections.defaultdict(dict)

    with uff.FortranFile(filename, 'rb', endian=endian) as f:

        for i in range(skip_rows):
            f.readline()

        while True:
            try:
                name = f.readline().strip()
                content = f.readline('ii*f')

                time = '%08d %06d' % content[:2]
                time = datetime.datetime.strptime(time, '%Y%m%d %H%M%S')

                values = numpy.array(content[2:])

                try:
                    values = values.reshape(SIZE2SHAPE[values.size], order='F')
                except KeyError, ValueError:
                    pass

                data[name][time] = values

            except EOFError:
                break

    return data
