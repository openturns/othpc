#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari
"""

import openturns as ot
from wrapper_jobarray import SLURMJobArrayWrapper
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
my_wrapper = SLURMJobArrayWrapper(input_dimension=X.getDimension(), output_dimension=1, index_col=0)
my_wrapper.slurm_resources = {
"nodes-per-job": 1,
"cpus-per-job": 4,
"mem-per-job": 1024, # 1024 MB
"timeout": "00:30:00", # 30 minutes
"nb-jobs": 4
}
g = my_wrapper.get_function(previous_evals_file="beam_evals.pkl")
Y = g(X)
XY = my_wrapper.make_inputoutput_file(g, X)
print(XY)