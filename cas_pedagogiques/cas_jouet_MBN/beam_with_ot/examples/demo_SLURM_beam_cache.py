#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

A demonstration of the SLURMJobArrayFunction class on the beam 
example with the MemoizeWithCSVFile.

The model is evaluated pointwise.
This allows to use a intput/output cache file pair.
Hence, if the job does not go to its end (e.g. if the time is limited),
then it suffices to re-run the sbatch command.
In this case, if any point has already been evaluated inside a 
local simulation directory, then the evaluation will be instantaneous.
"""

# %%
import os
import openturns as ot
import openturns.testing as ott
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
beam_no_cache = ot.Function(beamModel)

# %%
# Use a cache (this is the purpose of this example)
beam_with_cache = otcluster.MemoizeWithCSVFile(
    beam_no_cache, "input_cache.csv", "output_cache.csv", verbose=True
)
model = ot.Function(beam_with_cache)

# %%
# Input sample
block_size = 20  # This uses sub-samples of maximum size equal to 100
number_of_jobs = 10
sampleSize = number_of_jobs * block_size
print(f"block_size = {block_size}")
print(f"number_of_jobs = {number_of_jobs}")
print(f"sampleSize = {sampleSize}")
input_sample = X_distribution.getSample(sampleSize)

# %%
# Define SLURM function (no cache)
print("+ Define SLURM function (no cache)")
sbatch_wckey = "P120F:PYTHON"
user_resources = [
    os.path.join(cwd, "BeamFunction.py"),
    os.path.join(
        cwd, "otcluster", "MemoizeWithCSVFile.py"
    ),  # TODO : can we avoid to copy this resource?
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

# %%
# Evaluate the model pointwise, with cache
print("+ Evaluate the model pointwise, with cache")
slurm_machine = otcluster.SLURMJobArrayMachine(
    model,
    sbatch_wckey,
    user_resources=user_resources,
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    block_size=block_size,
    verbose=True,
)
slurm_wrapper = otcluster.SLURMJobArrayFunction(slurm_machine, verbose=True)
print("+ Evaluate model")
output_sample = slurm_wrapper(input_sample)
print("output_sample = ")
print(output_sample)
# Compare with the straightforward model to check the order to the points
Y_model = model(input_sample)
print("Y_model =")
print(Y_model)
# Check for equality
data_SLURM = ot.Sample(input_sample)
data_SLURM.stack(output_sample)
data_model = ot.Sample(input_sample)
data_model.stack(Y_model)
print("data_SLURM =")
print(data_SLURM)
print("data_model =")
print(data_model)
ott.assert_almost_equal(output_sample, Y_model)
