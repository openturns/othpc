#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré

A demonstration of the MemoizeWithCSVFile class on the beam example.

Example
-------
$ python3 demo_MemoizeWithCSVFile.py

"""
# %%
import os
import openturns as ot
import otcluster
import openturns.testing as ott
import time
from BeamFunction import BeamFunction


def check_input_output_csv(
    input_sample_reference,
    output_sample_reference,
    input_cache_csv_filename,
    output_cache_csv_filename,
):
    # Check csv. Caution: the order of the points in the CSV is different
    # because the std::map has no particular reason to keep the order.
    # Indeed, the contract is to save points, but not the order.
    # Therefore, we do not make a straightforward comparison between the
    # samples: we sort them before.
    input_sample_csv = ot.Sample.ImportFromCSVFile(input_cache_csv_filename)
    output_sample_csv = ot.Sample.ImportFromCSVFile(output_cache_csv_filename)
    print("input_sample_csv:")
    print(input_sample_csv)
    print("output_sample_csv:")
    print(output_sample_csv)
    # Sort CSV samples (X, Y) pairs
    indices = output_sample_csv.argsort()
    input_sample_csv_sorted = input_sample_csv[indices]
    output_sample_csv_sorted = output_sample_csv[indices]
    # Sort reference samples (X, Y) pairs
    indices = output_sample_reference.argsort()
    input_sample_reference_sorted = input_sample_reference[indices]
    output_sample_reference_sorted = output_sample_reference[indices]
    ott.assert_almost_equal(input_sample_csv_sorted, input_sample_reference_sorted)
    ott.assert_almost_equal(output_sample_csv_sorted, output_sample_reference_sorted)


# %%
# Cleanup (otherwise we always use the cache!)
if os.path.isfile("input_cache.csv") or os.path.isfile("output_cache.csv"):
    raise ValueError(
        "The input_cache.csv or output_cache.csv already exist on disk. "
        "Please remove them or the demonstration cannot pass."
    )

# %%
# Create beam model
print("Create beam model")
simulation_directory = os.getcwd()
input_template_filename = os.path.join(simulation_directory, "beam_input_template.xml")
beam_executable = os.path.join(simulation_directory, "beam")
beamModel = BeamFunction(
    input_template_filename, beam_executable, sleep=0.1, verbose=False
)
input_distribution = beamModel.getInputDistribution()
model = ot.Function(beamModel)

# %%
# Input sample
sampleSize = 5
input_sample = input_distribution.getSample(sampleSize)
model = ot.Function(beamModel)
output_sample_reference = model(input_sample)

# %%
# Define function (with cache)
beam_with_cache = otcluster.MemoizeWithCSVFile(
    model, "input_cache.csv", "output_cache.csv", verbose=False
)
print("1. Evaluate sample")
t1 = time.time()
output_sample = beam_with_cache(input_sample)
t2 = time.time()
time_initial = t2 - t1
print(f"Elapsed = {time_initial} (s)")
# Check
ott.assert_almost_equal(output_sample, output_sample_reference)
print("output_sample = ")
print(output_sample)
check_input_output_csv(
    input_sample, output_sample_reference, "input_cache.csv", "output_cache.csv"
)

# %%
print("2. Evaluate sample")
t1 = time.time()
output_sample = beam_with_cache(input_sample)  # This should be instantaneous
t2 = time.time()
time_with_cache = t2 - t1
print(f"Elapsed = {time_with_cache} (s)")
assert time_with_cache < time_initial / 10.0
print("output_sample = ")
print(output_sample)
# Check
ott.assert_almost_equal(output_sample, output_sample_reference)

# %%
# Create input sample, larger
# Hence, the new points are not in cache.
sampleSize = 10
input_sample = input_distribution.getSample(sampleSize)
output_sample_reference = model(input_sample)

# %%
# Define function (with cache)
beam_with_cache = otcluster.MemoizeWithCSVFile(
    model, "input_cache.csv", "output_cache.csv", verbose=False
)
print("1. Evaluate sample")
t1 = time.time()
output_sample = beam_with_cache(input_sample)
t2 = time.time()
time_initial = t2 - t1
print(f"Elapsed = {time_initial} (s)")
print("output_sample = ")
print(output_sample)
# Check
ott.assert_almost_equal(output_sample, output_sample_reference)
print("2. Evaluate sample")
t1 = time.time()
output_sample = beam_with_cache(input_sample)  # This should be instantaneous
t2 = time.time()
time_with_cache = t2 - t1
print(f"Elapsed = {time_with_cache} (s)")
assert time_with_cache < time_initial / 10.0
print("output_sample = ")
print(output_sample)
# Check
ott.assert_almost_equal(output_sample, output_sample_reference)

# %%
# Re-Define function (with cache)
beam_with_cache = otcluster.MemoizeWithCSVFile(
    model, "input_cache.csv", "output_cache.csv", verbose=False
)
print("3. Evaluate sample")
output_sample = beam_with_cache(input_sample)  # This should be instantaneous
print("output_sample = ")
print(output_sample)

# %%
# Cleanup (otherwise we always use the cache!)
os.remove("input_cache.csv")
os.remove("output_cache.csv")

# %%
