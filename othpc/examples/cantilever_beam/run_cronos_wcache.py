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

input_template_file = "template/beam_input_template.xml"
executable_file = "template/beam"
my_results_directory = "my_results"
try:
    os.mkdir(my_results_directory)
except FileExistsError:
    pass
cb = CantileverBeam(input_template_file, executable_file, my_results_directory)
dw = othpc.DaskFunction(cb)
dwfun = ot.Function(dw)
memoize_dwfun = ot.MemoizeFunction(dwfun)
# load the cache from the summary file
summary_data = ot.Sample.ImportFromCSVFile(
    os.path.join(my_results_directory, "summary_table.csv")
)
# add the cache to the function
input_cache = summary_data[:, : dwfun.getInputDimension()]
output_cache = summary_data[:, dwfun.getInputDimension() :]
memoize_dwfun.addCacheContent(input_cache, output_cache)
#
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
Y = memoize_dwfun(X)
print(Y)
