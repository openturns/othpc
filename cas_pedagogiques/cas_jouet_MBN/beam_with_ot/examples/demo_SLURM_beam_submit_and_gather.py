#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

A demonstration of the SLURMJobArrayMachine class on the beam 
example:
1. Submit the job (connect),
2. Disconnect the computer,
3. Wait and gather the results.
"""

# %%
import os
import openturns as ot
import pickle
import time
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
# Input sample
sampleSize = 10
X = X_distribution.getSample(sampleSize)

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

# Part 1: launch job, and disconnect
slurm_machine = otcluster.SLURMJobArrayMachine(
    model,
    sbatch_wckey,
    user_resources=user_resources,
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    verbose=True,
)
print("slurm_machine = ")
print(slurm_machine)
job = slurm_machine.create(X)
command = slurm_machine.submit()
print(f"command = {command}")

# Save job on disk
with open("job.pkl", "wb") as f:
    pickle.dump(job, f)

# Disconnect

# Part 2: reconnect to job, and wait
with open("job.pkl", "rb") as f:
    job = pickle.load(f)

print("job = ")
print(job)

print(f"Gathering results from {job.results_directory}.")

# Wait 60 seconds or less
tempo = 0.0
timeout = 60.0
wait_time = 1.0
verbose = True
finished = False
while not finished and tempo < timeout:
    if verbose:
        print(f"Wait for results after {tempo}")
    tempo += wait_time
    time.sleep(wait_time)
    finished = job.is_finished()

if tempo >= timeout:
    raise ValueError(f"Waited more than {timeout} seconds: time out.")
else:
    print("Success!")

# The job is finished: get the X/Y pair.
X, Y = job.get_input_output(verbose=True)

print("X = ")
print(X)

print("Y = ")
print(Y)

# TODO : an option to delete the simulation directory
