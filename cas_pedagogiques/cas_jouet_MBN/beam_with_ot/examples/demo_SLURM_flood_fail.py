#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

A demonstration of the SLURMJobArrayFunction class on the flood model.
Uses a version of the flooding model which fails half of the times.

Example
-------
$ python3 demo_SLURM_flood_fail.py
"""

# %%
import os
import openturns as ot
import otcluster


class FloodModel:
    def __init__(
        self,
    ):
        """
        Create a flood model.

        This model has 4 inputs : (Q, Ks, Zv, Zm) and 1 output (S).
        """
        # Q
        self.Q = ot.TruncatedDistribution(
            ot.Gumbel(558.0, 1013.0), 0.0, ot.TruncatedDistribution.LOWER
        )
        self.Q.setName("Q")
        self.Q.setDescription(["Q (m3/s)"])

        # Ks
        self.Ks = ot.TruncatedDistribution(
            ot.Normal(30.0, 7.5), 0.0, ot.TruncatedDistribution.LOWER
        )
        self.Ks.setName("Ks")
        self.Ks.setDescription(["Ks"])

        # Zv
        # self.Zv = ot.Uniform(49.0, 51.0)  # OK
        self.Zv = ot.Uniform(49.0, 56.0)
        self.Zv.setName("Zv")
        self.Zv.setDescription(["Zv (m)"])

        # Zm
        # self.Zm = ot.Uniform(54.0, 56.0)  # OK
        self.Zm = ot.Uniform(49.0, 56.0)
        self.Zm.setName("Zm")
        self.Zm.setDescription(["Zm (m)"])

        self.distribution = ot.ComposedDistribution([self.Q, self.Ks, self.Zv, self.Zm])

        def model(X):
            from math import sqrt

            Q, Ks, Zv, Zm = X
            Hd = 3.0
            Zb = 55.5
            L = 5.0e3
            B = 300.0
            Zd = Zb + Hd
            alpha = (Zm - Zv) / L
            H = (Q / (Ks * B * sqrt(alpha))) ** (3.0 / 5.0)
            Zc = H + Zv
            S = Zc - Zd
            return [S]

        self.model = ot.PythonFunction(4, 1, model)
        self.model.setInputDescription(["Q", "Ks", "Zv", "Zm"])
        self.model.setOutputDescription(["S"])


# %%
# Create beam model
print("Create beam model")
floodModel = FloodModel()

# %%
# Input sample
sampleSize = 20
X = floodModel.distribution.getSample(sampleSize)
print("X = ")
print(X)
# Check single evaluation:
print(f"X[0] = {X[0]}")
print(floodModel.model(X[0]))

# %%
# Case 1: Define SLURM function (no cache)
print("Case 1 : Define SLURM function (no cache)")
cwd = os.getcwd()
sbatch_wckey = "P120F:PYTHON"
base_directory = os.getcwd()
sbatch_extra_options = (
    '--output="logs/output.log" '
    '--error="logs/error.log" '
    "--nodes=1 "
    "--cpus-per-task=1 "
    "--mem=512 "
    '--time="00:05:00"'
)
slurm_machine = otcluster.SLURMJobArrayMachine(
    floodModel.model,
    sbatch_wckey,
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    verbose=True,
)
slurm_wrapper = otcluster.SLURMJobArrayFunction(slurm_machine, verbose=True)
slurm_function = ot.Function(slurm_wrapper)
print("Evaluate model")
Y = slurm_wrapper(X)
print("Y = ")
print(Y)
