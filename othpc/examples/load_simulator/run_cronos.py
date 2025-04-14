#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import othpc
import openturns as ot
from MPILoadSimulator import MPILoadSimulator

cb = MPILoadSimulator(simu_duration=60)

dw = othpc.DaskFunction(cb, cpus_per_job=1, job_number=3, timeout_per_job=10, verbose=True)
# dwfun = ot.Function(dw)
X = ot.Sample.ImportFromCSVFile("input_doe/doe_small.csv", ",")
Y = dw(X[:3])
print(Y)
# othpc.make_summary_file("my_results", summary_file="summary_table.csv")