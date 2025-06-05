#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import os
import othpc
import pandas as pd
import openturns as ot
from cantilever_beam import CantileverBeam

my_results_directory = "my_results"
cb = CantileverBeam(my_results_directory, n_cpus=2)
dw = othpc.SubmitFunction(cb, tasks_per_job=2, cpus_per_job=2, timeout_per_job=5)
dwfun = ot.Function(dw)
memoize_dwfun = othpc.load_cache(
    dwfun, os.path.join(my_results_directory, "summary_table.csv")
)
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
Y = memoize_dwfun(X)
print(Y)
