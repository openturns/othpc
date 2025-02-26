#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@author: Elias Fekhari
"""

import time
import openturns as ot
from itertools import product 
from dask_jobqueue import SLURMCluster
from dask.distributed import Client, progress

def function(X):
    return [X[0] + X[1]]

ot_function = ot.PythonFunction(2, 1, function)

# Define dask SLURM cluster
cluster = SLURMCluster(cores=4, memory="512 MB", job_extra_directives=['--wckey=p127z:datascience', '--time=5', '--output=wrapper.log', '--error=wrapper_error.log'])
cluster.scale(2) # Creates two jobs with the specs above
# Define dask client 
client = Client(cluster)

print(client)
time.sleep(30)
print(client)

futures = []
for x1, x2 in product(range(3), range(3)):
    print(x1, x2)
    X = [x1, x2]
    future = client.submit(ot_function, X)
    futures.append(future)
print(futures[0].status)
results = client.gather(futures)
print(results)
print(futures[0].status)
