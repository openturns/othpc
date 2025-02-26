#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

A demonstration of the FunctionInsideDirectory class on the beam example.

Example
-------
$ python3 demo_beam_inside_directory.py
"""
# %%
import os
import openturns as ot
from BeamFunction import BeamFunction
import otcluster
from datetime import datetime
from openturns.func import _exec_sample_multiprocessing_func

# %%
print("Create the BeamFunction")
simulation_directory = os.getcwd()
input_template_filename = os.path.join(simulation_directory, "beam_input_template.xml")
beam_executable = os.path.join(simulation_directory, "beam")
beamFunction = BeamFunction(input_template_filename, beam_executable, verbose=True)
model = ot.Function(beamFunction)
main_directory = "work_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
modelInsideDir = otcluster.FunctionInsideDirectory(
    model, main_directory, cleanup_on_delete=False, verbose=True
)
functionInsideDir = ot.Function(modelInsideDir)
multiprocessing_fun = _exec_sample_multiprocessing_func(functionInsideDir, 6) # run on 6 cores
print("Create X sample")
input_distribution = beamFunction.getInputDistribution()
sample_size = 5000
input_sample = input_distribution.getSample(sample_size)
print("X = ")
print(input_sample)
print("Compute Y")
output_sample = multiprocessing_fun(input_sample)
print("Y = ")
print(output_sample)
del multiprocessing_fun, functionInsideDir, modelInsideDir

# %%
