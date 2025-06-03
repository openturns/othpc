#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import os
import othpc
import openturns as ot
from cantilever_beam import CantileverBeam
from openturns.usecases import cantilever_beam

input_template_file = "template/beam_input_template.xml"
executable_file = "template/beam"
my_results_directory = "my_results_algorithm"
try:
    os.mkdir(my_results_directory)
except FileExistsError:
    pass
cpus_per_jobs = 2
cb = CantileverBeam(input_template_file, executable_file, my_results_directory, n_cpus=cpus_per_jobs)
dw = othpc.SubmitItFunction(cb, tasks_per_job=cpus_per_jobs, cpus_per_job=cpus_per_jobs, timeout_per_job=5)
dwfun = ot.Function(dw)

# Load distributions from the OpenTURNS CantileverBeam example
openturns_example = cantilever_beam.CantileverBeam()
distribution = openturns_example.distribution
distribution.setDescription(["E", "F", "L", "I"])
vect = ot.RandomVector(distribution)
Yvect = ot.CompositeRandomVector(dwfun, vect)
# Build ExpectedSimulationAlgorithm
algo = ot.ExpectationSimulationAlgorithm(Yvect)
algo.setMaximumOuterSampling(3)
algo.setBlockSize(cpus_per_jobs)
algo.setMaximumCoefficientOfVariation(-1.0)
algo.run()
result = algo.getResult()
expectation = result.getExpectationEstimate()
print(expectation)
