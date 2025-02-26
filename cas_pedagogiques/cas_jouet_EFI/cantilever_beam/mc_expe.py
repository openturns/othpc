#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari
"""

import openturns as ot
from openturns.usecases import cantilever_beam
from wrapper_jobarray import SLURMJobArrayWrapper


# Load distributions from the OpenTURNS CantileverBeam example 
cb = cantilever_beam.CantileverBeam()
distribution = cb.distribution
distribution.setDescription(["E", "F", "L", "I"])
dim = distribution.getDimension()

# Create a wrapper object
my_wrapper = SLURMJobArrayWrapper(input_dimension=dim, output_dimension=1)
g = my_wrapper.get_function()
# g = ot.Function(my_wrapper)


# Use the wrapper in an OpenTURNS algorithm
vect = ot.RandomVector(distribution)
Yvect = ot.CompositeRandomVector(g, vect)
algo = ot.ExpectationSimulationAlgorithm(Yvect)
algo.setMaximumOuterSampling(3)
algo.setBlockSize(10)
algo.setMaximumCoefficientOfVariation(0.01)  
algo.run()
result = algo.getResult()
expectation = result.getExpectationEstimate()

X = g.getCacheInput()
my_wrapper.make_inputoutput_file(g, X)

print(expectation)