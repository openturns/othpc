#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import othpc
import openturns as ot
from MPILoadSimulator import MPILoadSimulator

ls = MPILoadSimulator(nb_mpi_proc=64, simu_duration=180)
dls = othpc.DistributedMPIFunction(
    ls, ntasks_per_node=34, nodes_per_job=2, cpus_per_task=1, timeout_per_job=5, 
    # slurm_additional_parameters={"qos":"test"}
)
f = ot.Function(dls)
X = ot.Sample.ImportFromCSVFile("input_doe/doe_small.csv", ",")
Y = f(X[:3])
print(Y)
# othpc.make_summary_file("my_results", summary_file="summary_table.csv")
