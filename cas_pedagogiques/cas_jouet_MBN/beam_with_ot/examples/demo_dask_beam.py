#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

A demonstration of the DaskFunction on the beam example.

Examples
--------
Usage on Cronos:

$ module load Miniforge3
$ conda activate myenv  # With OpenTURNS
$ python demo_dask_beam.py

"""

# %%
import os
import openturns as ot
from BeamFunction import BeamFunction
from DaskFunction import DaskFunction
from FunctionInsideDirectory import FunctionInsideDirectory

# %%
# Create beam model
print("+ Create beam model")
cwd = os.getcwd()
# The two files input_template_filename and beam_executable are the same for
# all simulations: there is no copy of these files in each local simulation directory.
# This is because these files are read, but not written.
input_template_filename = os.path.join(
    cwd, "beam_input_template.xml"
)  # This file is in the current directory (not copied)
beam_executable = os.path.join(
    cwd, "beam"
)  # This file is in the current directory (not copied)
beamModel = BeamFunction(input_template_filename, beam_executable, verbose=True)
# Get the input distribution
X_distribution = beamModel.getInputDistribution()

# Wrap the model so that each evaluation is inside a temporary directory
# and all workers do not overlap each other
beamModelInsideDir = FunctionInsideDirectory(beamModel, verbose=True)

model = ot.Function(beamModelInsideDir)

# %%
# Input sample
sampleSize = 10
X = X_distribution.getSample(sampleSize)

# %%
# Case 1: Define SLURM function (no cache)
print("+ Case 1 : Define SLURM function (no cache)")
sbatch_wckey = "P120F:PYTHON"

# base_directory = "/scratch/users/C61372/beam"
base_directory = os.getcwd()
slurm_options = (
    '--output="logs/output.log" ' '--error="logs/error.log" ' '--time="00:05:00"'
)

slurm_model = DaskFunction(
    model,
    sbatch_wckey,
    slurm_options,
    dask_nb_jobs=sampleSize,
    verbose=True,
)
print("slurm_model = ")
print(slurm_model)
slurm_function = ot.Function(slurm_model)
print("slurm_function = ")
print(slurm_function)
print("+ Evaluate model")
Y = slurm_function(X)
print("Y = ")
print(Y)
