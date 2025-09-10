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
cb = CantileverBeam(my_results_directory, n_cpus=evals_per_job)
sf = othpc.SubmitFunction(
    cb, evals_per_job=evals_per_job, cpus_per_job=evals_per_job, timeout_per_job=5
)
f = ot.Function(sf)

# Load distributions from the OpenTURNS CantileverBeam example
openturns_example = cantilever_beam.CantileverBeam()
distribution = openturns_example.distribution
distribution.setDescription(["E", "F", "L", "I"])
print(f(distribution.getMean()))
vect = ot.RandomVector(distribution)
Yvect = ot.CompositeRandomVector(f, vect)
event = ot.ThresholdEvent(Yvect, ot.Greater(), 0.22)
standard_event = ot.StandardEvent(event)
standard_function = standard_event.getFunction()
print(standard_function([0.0] * 4))
print(standard_function.gradient([0.0] * 4))

# We create an OptimizationAlgorithm algorithm
solver = ot.AbdoRackwitz()
algo = ot.FORM(solver, event, distribution.getMean())
algo.run()
result = algo.getResult()

print(result)
