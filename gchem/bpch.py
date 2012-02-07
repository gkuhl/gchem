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
Reading and writing Binary Punch files (bpch)
"""

import datetime
import os

import numpy

import misc
import info
import uff


# tracerinfo.dat and diaginfo.dat
_dir_path = os.path.dirname(os.path.abspath(__file__))
CATEGORY2OFFSET, CATEGORY2COMMENT, TRACER2INFO = info.read(
    os.path.join(_dir_path, 'data', 'tracerinfo.dat'),
    os.path.join(_dir_path, 'data', 'diaginfo.dat')
)
del _dir_path


class DataBlock(object):

    def __init__(self, category, center180, halfpolar, modelname, number,
            origin, resolution, shape, times, unit, name=None,
            fullname=None, carbon_weight=None, molecular_weight=None,
            skip=None, file=None, position=None, values=None):
        """\
        The class presents a data block in a binary punch file.
        """

        self.modelname = modelname
        self.resolution = resolution
        self.halfpolar = halfpolar
        self.center180 = center180
        self.category = category
        self.number = number
        self.unit = unit
        self.times = times
        self.shape = tuple(shape)
        self.origin = tuple(origin)

        # information are loaded from "tracerinfo.dat" (if available)
        self.name = name
        self.full_name = fullname
        self.carbon_weight = carbon_weight
        self.molecular_weight = molecular_weight

        # position of data in file (will be loaded on request)
        self._position = position
        self._file = file
        self._values = values


    @property
    def size(self):
        return reduce(lambda x,y: x*y, self.shape)


    @property
    def value(self):
        if (self._values is None and self._file is not None
            and self._position is not None
        ):
            self._file.seek(self._position)
            value = numpy.array(self._file.readline('*f'))
            value = value.reshape(self.shape, order='F')
            self._values = value
        return self._values


    @value.setter
    def value(self, data):
        self._value = data


    def __repr__(self):

        # create time representive
        start, end = self.times
        time_fmt = '%Y-%m-%d %H:%M'
        time_repr = start.strftime(time_fmt)

        if start != end:
            time_repr = ' '.join([time_repr, '-', end.strftime(time_fmt)])

        # create name representive
        if self.name is None:
            name = '%s %s' % (self.number, self.category)
        else:
            name = '%s (%s) %s' % (self.name, self.number, self.category)

        return '<Datablock: %s; %s>' % (name, time_repr)



class File(object):

    def __init__(self, title='CTM Punch File by gchem',
            filetype='CTM bin 02', datablocks=None):
        """\
        A binary punch file: Can be used to create a punch file. To open an
        existing file, use the `File.fromfile` class method or the `open_file`
        function.

        Arguments:
        - title (default 'CTM Punch File by gchem')
        - filetype (default 'CTM bin 02')
        - datablocks: list of DataBlock objects or None (default)
        """
        # file attributes
        self.name = None
        self.mode = None
        self.size = None
        self._file = None
        self.endian = None

        # file content
        self.filetype = filetype
        self.title = title
        self.datablocks = datablocks if datablocks is not None else list()


    @classmethod
    def fromfile(cls, filename, mode='rb', endian='>', skip_values=False):
        """\
        Creates a binary punch file from a given filename.

        Arguments:
        - filename
        - mode (default 'rb')
        - endian (default '>')
        - skip values: If True only datablock headers will be read into
          memory and the values will read on request. Default: False.
        """
        cls = cls()

        cls.name = filename
        cls.mode = mode
        cls.datablocks = list()

        # read file header
        cls.size = os.path.getsize(filename)
        cls.endian = endian
        cls._file = uff.FortranFile(filename, mode, endian)
        cls.filetype = cls._file.readline().strip()
        cls.title = cls._file.readline().strip()

        while cls._file.tell() < cls.size:

            # read first and second header line
            line = cls._file.readline('20sffii')
            modelname, res0, res1, halfpolar, center180 = line
            line = cls._file.readline('40si40sdd40s7i')
            category, number, unit, tau0, tau1, reserved = line[:6]
            dim0, dim1, dim2, dim3, dim4, dim5, skip = line[6:]

            # skip datablock (read datablock if accessing value)
            position = cls._file.tell()
            if skip_values:
                cls._file.skipline()
                values = None
            else:
                values = numpy.array(cls._file.readline('*f'))
                values = values.reshape((dim0,dim1,dim2), order='F')

            # get addtional information
            offset = CATEGORY2OFFSET.get(category.strip(), None)
            if offset is None:
                info = {}
            else:
                info = TRACER2INFO.get(number+offset, {})

            # create DataBlock
            datablock = DataBlock(
                category = category.strip(),
                center180 = bool(center180),
                halfpolar = bool(halfpolar),
                modelname = modelname.strip(),
                number = number,
                origin = (dim3, dim4, dim5),
                resolution = (res0, res1),
                shape = (dim0, dim1, dim2),
                times = (misc.tau2time(tau0), misc.tau2time(tau1)),
                unit = unit.strip(),
                name = info.get('name', None),
                fullname = info.get('full_name', None),
                carbon_weight = info.get('c_weight', None),
                molecular_weight = info.get('molecular_weight', None),
                position = position,
                values = values,
                file = cls._file
            )

            cls.append(datablock)

        return cls


    @property
    def categories(self):
        return sorted(set(db.category for db in self.datablocks))


    def close(self):
        """\
        Close file (if open).
        """
        if self._file is not None:
            self._file.close()


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        if self._file is not None:
            self._file.__exit__(type, value, traceback)


    def __iter__(self):
        for obj in self.datablocks:
            yield obj

    def __len__(self):
        return len(self.datablocks)


    def __repr__(self):
        if self._file is None:
            return "<Binary Punch file in memory>"
        else:
            status = 'closed' if self._file.closed else 'open'
            string = "<%s Binary Punch file '%s', mode '%s' at %s>"
            return string % (status, self.name, self.mode, hex(id(self._file)))


    def filter(self, name=None, number=None, category=None, time=None,
            fmt='%Y-%m-%d'):
        """
        self.filter(name=None, number, category=None, time=None,
            fmt='%Y-%m-%d')

        Returns list of datablocks which meet 'name', 'category' and
        'time'. For 'time' a format can be used.
        """
        data = self.datablocks

        if name is not None:
            data = filter(lambda db: db.name == name, data)

        if number is not None:
            data = filter(lambda db: db.number == number, data)

        if category is not None:
            data = filter(lambda db: db.category == category, data)

        if time is not None:
            if isinstance(time, basestring):
                time = datetime.datetime.strptime(time, fmt)
            data = filter(lambda db: db.times[0] == time, data)

        return sorted(data)


    def append(self, datablock):
        """\
        append datablock
        """
        self.datablocks.append(datablock)


    def save_as(self, filename, endian='>'):
        """\
        Save Binary Punch file to `filename`.
        """
        with uff.FortranFile(filename, 'wb', endian) as out_file:
            # write header
            out_file.writeline('40s', self.filetype.ljust(40))
            out_file.writeline('80s', self.title.ljust(80))

            # write data blocks
            for b in self.datablocks:
                out_file.writeline('20sffii',
                    b.modelname.ljust(20), b.resolution[0],
                    b.resolution[1], b.halfpolar, b.center180
                )
                out_file.writeline('40si40s2d40s7i',
                    b.category.ljust(40), b.number, b.unit.ljust(40),
                    misc.time2tau(b.times[0]), misc.time2tau(b.times[1]),
                    ''.ljust(40), b.shape[0], b.shape[1], b.shape[2],
                    b.origin[0], b.origin[1], b.origin[2], b.size*4
                )
                out_file.writeline('%df' % b.size, *b.value.flatten('F'))


def open_file(filename, mode='rb', endian='>', skip_values=False):
    """\
    Open a binary punch file with given `filename` and `mode`
    (default 'rb').
    """
    return File.fromfile(filename, mode, endian, skip_values)


def make_restartfile(date, modelname='GEOS5_47L', n_tracers=43,
        origin=(0,0,0), tracer_numbers=None, resolution=(2.5,2.0),
        shape=(144,91,47)
    ):
    """\
    Create restart file.

    Example
    >>> create_restartfile(...).save_as(filename)
    """
    if tracer_numbers is None:
        tracer_numbers = range(1,n_tracers+1)

    datablocks = []
    for number in tracer_numbers:
        datablocks.append(
            DataBlock(
                category = 'IJ-AVG-$',
                center180 = True,
                halfpolar = True,
                modelname = modelname,
                number = number,
                origin = origin,
                resolution = resolution,
                shape = shape,
                times = (date, date),
                unit = 'v/v',
                values = numpy.zeros(shape)
            )
        )

    return File(datablocks=datablocks)

