#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

A demonstration of the SLURMJobArrayFunction class on the beam 
example.
Evaluates the DoE available in "input_doe.csv".
"""

# %%
import os
import openturns as ot
from BeamFunction import BeamFunction
import otcluster

# %%
# Create beam model
print("+ Create beam model")
cwd = os.getcwd()
input_template_filename = os.path.join(
    cwd, "beam_input_template.xml"
)  # This file is in the current directory (not copied)
beam_executable = os.path.join(
    cwd, "beam"
)  # This file is in the current directory (not copied)
beamModel = BeamFunction(input_template_filename, beam_executable)
X_distribution = beamModel.getInputDistribution()

# %%
# Define SLURM function (no cache)
print("+ Define SLURM function (no cache)")
model = ot.Function(beamModel)
sbatch_wckey = "P120F:PYTHON"
user_resources = [
    os.path.join(cwd, "BeamFunction.py"),
]

# base_directory = "/scratch/users/C61372/beam"
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
    model,
    sbatch_wckey,
    user_resources=user_resources,
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    verbose=True,
)
slurm_wrapper = otcluster.SLURMJobArrayFunction(slurm_machine, verbose=True)
slurm_function = ot.Function(slurm_wrapper)

# %%
# Evaluate a design of experiments already available on disk
print("+ Evaluate a design of experiments already available on disk")
X = ot.Sample.ImportFromCSVFile("input_doe.csv")
print("+ Evaluate model")
Y = slurm_function(X)
print("Y = ")
print(Y)
