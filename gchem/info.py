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
Functions for reading 'tracerinfo.dat' and 'diaginfo.dat'.
"""

def read_fixed_format(string, format):
    """\
    Converts `string` with given `format` to dictionary.
    """
    return dict((name, function( string[i:i+di].strip()))
                        for name, i, di, function in format)


def read_tracerinfo(filename):
    """\
    Read a 'tracerinfo.dat'-file with given `filename`.
    """
    format = [
        ('name', 0, 8, str),
        ('full_name', 9, 30, str),
        ('molecular_weight', 39, 10, float),
        ('c_weight', 49, 3, int),
        ('number', 52, 9, int),
        ('scale', 61, 10, float),
        ('unit', 72, 40, str)
    ]
    with open(filename, 'r') as file_obj:
        tracerinfo = (read_fixed_format(line, format)
                for line in file_obj if not line.startswith('#'))
        return dict( (row['number'], row) for row in tracerinfo)


def read_diaginfo(filename):
    """\
    Read 'diaginfo.dat'-file with given `filename`.
    """
    format = [
        ('offset',   0,  8, int),
        ('category', 9, 40, str),
        ('comment', 49, -1, str)
    ]
    with open(filename, 'r') as file_obj:
        diaginfo = (read_fixed_format(line, format) for line in file_obj
                        if not line.startswith('#'))
        cat2off = dict( ( row['category'], row['offset']) for row in diaginfo)
        cat2com = dict( ( row['category'], row['comment']) for row in diaginfo)

    return cat2off, cat2com


def read(tracerinfo, diaginfo):
    """\
    Returns the following dicts `category2offset`,`category2comment`
    and `tracer2info`.
    """
    category2offset, category2comment = read_diaginfo(diaginfo)
    tracer2info = read_tracerinfo(tracerinfo)

    return category2offset, category2comment, tracer2info



