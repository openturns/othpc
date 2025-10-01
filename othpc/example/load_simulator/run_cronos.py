#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import othpc
import openturns as ot
from MPILoadSimulator import MPILoadSimulator

cb = MPILoadSimulator(
    nb_mpi_proc=10, nb_slurm_nodes=2, simu_duration=2, slurm_timeout=5
)
sf = othpc.SubmitFunction(cb, timeout_per_job=5)
f = ot.Function(sf)
X = ot.Sample.ImportFromCSVFile("input_doe/doe_small.csv", ",")
Y = f(X[:3])
print(Y)
# othpc.make_summary_file("my_results", summary_file="summary_table.csv")
