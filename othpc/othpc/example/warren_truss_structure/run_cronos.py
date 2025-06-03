#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari
"""
import othpc
import openturns as ot
from template.truss_fem_model import warren_truss_displacement

# Material and section properties
E = ot.LogNormalMuSigma(2.1e11, 2.1e10).getDistribution() # Young's modulus (Pa)
A = ot.LogNormalMuSigma(0.01, 0.001).getDistribution()       # Cross-sectional area (m^2)
P = ot.Normal(-2000, 200)  # uniform load applied uniformally per node (in N, downward)
# max_node, max_disp, displacemenents = warren_truss_displacement(E, A, P)

distribution = ot.JointDistribution([E, A, P])
X = distribution.getSample(int(5))
truss_model = ot.PythonFunction(3, 1, warren_truss_displacement)
slurm_truss_model = othpc.SubmitItFunction(truss_model, tasks_per_job=1, cpus_per_job=1, timeout_per_job=1)
Y = slurm_truss_model(X)
print(Y)