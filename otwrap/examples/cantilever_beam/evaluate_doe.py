#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari
"""

import os
import openturns as ot
import openturns.coupling_tools as otct
from xml.dom import minidom
from otwrap import SLURMJobArrayWrapper

X = ot.Sample.ImportFromCSVFile("doe.csv", ",")
my_wrapper = SLURMJobArrayWrapper(input_dimension=X.getDimension(), output_dimension=1, index_col=0)

# Overriding the replace() method
def replace(X, r, xsimu_dir):
        otct.replace(
            # File template including your tokens to be replaced by values from a design of exp.
            os.path.join(my_wrapper.work_dir, 'template/beam_input_template.xml'),
            # File written after replacing the tokens by the values in X
            os.path.join(xsimu_dir, 'beam_input.xml'),
            ['@F@', '@E@', '@L@', '@I@'],
            X[r, :]
            )
my_wrapper.replace = replace

# Overriding the parse_output() method
def parse_output(xsimu_dir): 
    xmldoc = minidom.parse(os.path.join(xsimu_dir, '_beam_outputs_.xml'))
    itemlist = xmldoc.getElementsByTagName('outputs')
    y = float(itemlist[0].attributes['deviation'].value)
    return y
my_wrapper.parse_output = parse_output

g = my_wrapper.get_function()
Y = g(X)
XY = my_wrapper.make_inputoutput_file(g, X)
print(XY)