#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import othpc
import openturns as ot
from MPILoadSimulator import MPILoadSimulator

cb = MPILoadSimulator(executable_file="./bin/myMPIProgram", nb_proc=80, simu_duration=30)
dw = othpc.DaskFunction(cb, nodes_per_job=2, cpus_per_job=40, job_number=2, verbose=True)
# dwfun = ot.Function(dw)
X = ot.Sample.ImportFromCSVFile("input_doe/doe_small.csv", ",")
Y = dw(X[:2])
print(Y)
# othpc.make_summary_file("my_results", summary_file="summary_table.csv")