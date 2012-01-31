#! /usr/bin/env python
# coding: utf-8

from datetime import datetime
import numpy as np
import gchem

# create restart file
f = gchem.bpch.make_restartfile(datetime(2010,1,1))

# fill datablock with index 25 (SO2) with random variables and print profile
n,m,l = f.datablocks[25].shape
f.datablocks[25].value[:] = np.random.rand(n,m,l)
print f.datablocks[25].value[4,12,:]
print

# save restart file to disk
f.save_as('restart_test.bin')


# open restart file again and filter for SO2
with gchem.bpch.open_file('./restart_test.bin') as f:
    so2 = f.filter('SO2')[0]

    # print some information and print the same profile
    print so2
    print 'name:', so2.full_name
    print 'molecular weight:', so2.molecular_weight
    print 'time:', so2.times[0]
    print so2.value[4,12,:]
