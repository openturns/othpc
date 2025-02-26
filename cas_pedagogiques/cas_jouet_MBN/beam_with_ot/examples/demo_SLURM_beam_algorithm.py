#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

A demonstration of the SLURMJobArrayFunction on the beam example,
within an OpenTURNS algorithm.
The chosen algorithm is ExpectationSimulationAlgorithm.

Examples
--------
$ python demo_SLURM_beam_algorithm.py
"""

# %%
import os
import openturns as ot
import sys
from BeamFunction import BeamFunction
import otcluster

# %%
# Create beam beamFunction
print("+ Create beam beamFunction")
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
beamFunction = ot.Function(beamModel)
sbatch_wckey = "P120F:PYTHON"
user_resources = [
    os.path.join(cwd, "BeamFunction.py"),
]
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
# Use within an algorithm
print("+ Use within an algorithm")
slurm_machine = otcluster.SLURMJobArrayMachine(
    beamFunction,
    sbatch_wckey,
    user_resources=user_resources,
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    verbose=True,
)
slurm_wrapper = otcluster.SLURMJobArrayFunction(slurm_machine, verbose=True)
slurm_function = ot.Function(slurm_wrapper)
inputRandomVector = ot.RandomVector(X_distribution)
outputRandomVector = ot.CompositeRandomVector(slurm_function, inputRandomVector)
algo = ot.ExpectationSimulationAlgorithm(outputRandomVector)
algo.setMaximumOuterSampling(100)
algo.setBlockSize(20)  # The number of nodes/CPUs we usually have.
algo.setMaximumCoefficientOfVariation(0.01)  # 1% C.O.V.


def report_progress(progress):
    sys.stderr.write("-- progress=" + str(progress) + "%\n")


algo.setProgressCallback(report_progress)
algo.run()
result = algo.getResult()
expectation = result.getExpectationEstimate()
print(f"Expectation = {expectation[0]}")
expectationDistribution = result.getExpectationDistribution()
alpha = 0.95
interval = expectationDistribution.computeBilateralConfidenceInterval(alpha)
print(f"interval = {interval}")

# %%
#
print("+ Compare with raw function")
outputRandomVector = ot.CompositeRandomVector(beamFunction, inputRandomVector)
algo = ot.ExpectationSimulationAlgorithm(outputRandomVector)
algo.setMaximumOuterSampling(100)
algo.setBlockSize(20)  # The number of nodes/CPUs we usually have.
algo.setMaximumCoefficientOfVariation(0.01)  # 1% C.O.V.
algo.setProgressCallback(report_progress)
algo.run()
result = algo.getResult()
expectation = result.getExpectationEstimate()
print(f"Expectation = {expectation[0]}")
expectationDistribution = result.getExpectationDistribution()
alpha = 0.95
interval = expectationDistribution.computeBilateralConfidenceInterval(alpha)
print(f"interval = {interval}")
