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
A Python Script Collection for GEOS-Chem Chemistry Transport Model

This module provides functions and classes for reading and writing (binary)
files used with the GEOS-Chem CTM.

Submodules for reading and writing:
- gchem.bpch: Reading and writing files in the binary punch format.
- gchem.info: Reading 'tracerinfo.dat' and 'diaginfo.dat'
- gchem.uff: Reading and writing unformatted Fortran Files.

Other modules:
- gchem.misc: Some routines for working with times, reading GMAO met fields.
- gchem.grids: Collection of grids used by GEOS-Chem.

"""

import bpch
import info
import uff
import misc
import grids

