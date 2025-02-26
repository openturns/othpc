#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

Use SLURMJobArrayFunction on a symbolic function. 

See  demo_SLURMJobArrayFunction.py for more details.

Example
-------
$ python3 demo_SLURM_ishigami.py
"""

# %%
import os
import openturns as ot
import otcluster
from openturns.usecases import ishigami_function

# %%
# Create Ishigami model
print("Create Ishigami model")
im = ishigami_function.IshigamiModel()

# %%
# Input sample
sampleSize = 10
X = im.distributionX.getSample(sampleSize)

# %%
print("Case 1 : Define SLURM function")
model = ot.Function(im.model)
cwd = os.getcwd()
sbatch_wckey = "P120F:PYTHON"
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
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    verbose=True,
)
slurm_wrapper = otcluster.SLURMJobArrayFunction(slurm_machine, verbose=True)
slurm_function = ot.Function(slurm_wrapper)
print("Evaluate model")
Y = slurm_wrapper(X)
print("Y = ")
print(Y)
