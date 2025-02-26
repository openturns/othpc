#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

A demonstration of the SLURMJobArrayFunction class on the beam 
example.

Examples
--------
Usage on Cronos:

$ module load Miniforge3
$ conda activate myenv  # With OpenTURNS
$ python demo_SLURM_beam.py

Adding the "nohup" option allows to run the python process in a background on one frontal HPC node, even after a disconnection:
Usage 2: "nohup python -u demo_SLURMJobArrayFunction.py 2>&1 &"
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
# The two files input_template_filename and beam_executable are the same for
# all simulations: there is no copy of these files in each local simulation directory.
# This is because these files are read, but not written.
input_template_filename = os.path.join(
    cwd, "beam_input_template.xml"
)  # This file is in the current directory (not copied)
beam_executable = os.path.join(
    cwd, "beam"
)  # This file is in the current directory (not copied)
beamModel = BeamFunction(input_template_filename, beam_executable)
model = ot.Function(beamModel)  # Conversion en `ot.Function`
X_distribution = beamModel.getInputDistribution()

# %%
# Input sample
sampleSize = 10
X = X_distribution.getSample(sampleSize)

# %%
# Case 1: Define SLURM function (no cache)
print("+ Case 1 : Define SLURM function (no cache)")
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
slurm_model = otcluster.SLURMJobArrayFunction(
    slurm_machine, timeout=5 * 60.0, verbose=True
)
print("slurm_model = ")
print(slurm_model)
slurm_function = ot.Function(slurm_model)  # Conversion en `ot.Function`
print("+ Evaluate model")
Y = slurm_function(X)
print("Y = ")
print(Y)

# %%
# Save cache on disk
print("+ Save cache on disk")
input_cache_filename = "input_cache.csv"
output_cache_filename = "output_cache.csv"
X.setDescription(slurm_function.getInputDescription())
X.exportToCSVFile(input_cache_filename)
Y.setDescription(slurm_function.getOutputDescription())
Y.exportToCSVFile(output_cache_filename)

# %%
# Case 2: Define SLURM function class (with cache)
print("+ Case 2 : Define Wrapper class (with cache)")
slurm_wrapper_with_cache = otcluster.MemoizeWithCSVFile(
    slurm_function, input_cache_filename, output_cache_filename
)
Y = slurm_wrapper_with_cache(X)  # This should be instantaneous
