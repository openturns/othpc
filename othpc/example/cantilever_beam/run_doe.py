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
evals_per_job = 2
cb = CantileverBeam(my_results_directory, n_cpus=1, fake_load_time=10)

sf = othpc.SubmitFunction(
    cb,
    ntasks_per_node=evals_per_job,
    nodes_per_job=1,
    cpus_per_task=1,
    timeout_per_job=5,
)
f = ot.Function(sf)
#
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")[0:9]
Y = f(X)
print(Y)
othpc.make_summary_file("my_results", summary_file="summary_table.csv")
