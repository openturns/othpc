#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import othpc
import openturns as ot
from othpc.example import CantileverBeam

my_results_directory = "my_results"
cb = CantileverBeam(my_results_directory, n_cpus=2)

sf = othpc.SubmitFunction(cb, evals_per_jobs=2, cpus_per_job=2, timeout_per_job=5)
f = ot.Function(sf)
#
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
Y = f(X)
print(Y)
othpc.make_summary_file("my_results", summary_file="summary_table.csv")
