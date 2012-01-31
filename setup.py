#! /usr/bin/env python
# coding: utf-8

from distutils.core import setup

files = ["data/*"]

setup(
    name                = 'gchem',
    version             = '0.1.0',
    description         = 'Read and write files from GEOS-Chem chemistry transport model',
    long_description    = """
    Module for reading and writing input/output files from the GEOS-Chem chemistry
    transport model.""",
    url                 = '',
    download_url        = '',
    author              = 'Gerrit Kuhlmann',
    author_email        = 'gerrit.kuhlmann@gmail.com',
    platforms           = ['any'],
    license             = 'GNU3',
    keywords            = ['python', 'GEOS Chem'],
    classifiers         = ['Development Status :: Beta',
                           'Intended Audiance :: Science/Research',
                           'License :: GNU version 3',
                           'Operating System :: OS Independent'
                          ],
    packages            = ['gchem'],
    package_data        = {'gchem': files}
)
