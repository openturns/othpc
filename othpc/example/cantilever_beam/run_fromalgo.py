#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import othpc
import openturns as ot
from othpc.example import CantileverBeam
from openturns.usecases import cantilever_beam

my_results_directory = "my_results_algorithm"
evals_per_job = 2
cb = CantileverBeam(my_results_directory, fake_load_time=1)
df = othpc.DistributedFunction(
    cb, ntasks_per_node=evals_per_job, timeout_per_job=5
)
f = ot.Function(df)

# Load distributions from the OpenTURNS CantileverBeam example
openturns_example = cantilever_beam.CantileverBeam()
distribution = openturns_example.distribution
distribution.setDescription(["E", "F", "L", "I"])
vect = ot.RandomVector(distribution)
Yvect = ot.CompositeRandomVector(f, vect)
# Build ExpectedSimulationAlgorithm
algo = ot.ExpectationSimulationAlgorithm(Yvect)
algo.setMaximumOuterSampling(3)
algo.setBlockSize(evals_per_job)
algo.setMaximumCoefficientOfVariation(-1.0)
algo.run()
result = algo.getResult()
expectation = result.getExpectationEstimate()
print(expectation)
