#!/usr/bin/env python

"""
General purpose OpenTURNS python wrapper
"""

__all__ = ['X_distribution']

import openturns as ot
import os

sample_E = ot.Sample.ImportFromCSVFile(
    os.path.join(os.path.dirname(__file__), "sample_E.csv"))
kernel_smoothing = ot.KernelSmoothing(ot.Normal())
bandwidth = kernel_smoothing.computeSilvermanBandwidth(sample_E)
E = kernel_smoothing.build(sample_E, bandwidth)
E.setDescription(['Young modulus'])

F = ot.LogNormalMuSigma(30000.0, 9000.0, 15000.0).getDistribution()
F.setDescription(['Load'])

L = ot.Uniform(250, 260)
L.setDescription(['Length'])

II = ot.Beta(2.5, 4, 310, 450)
II.setDescription(['Inertia'])

marginal_distributions = [F, E, L, II]

SR_cor = ot.CorrelationMatrix(len(marginal_distributions))
SR_cor[2, 3] = -0.2
copula = ot.NormalCopula(ot.NormalCopula.GetCorrelationFromSpearmanCorrelation(SR_cor))

X_distribution = ot.ComposedDistribution(marginal_distributions, copula)

x_sample = X_distribution.getSample(100)
xdf = x_sample.asDataFrame()
xdf = xdf.round(2)
print(xdf) 
xdf.to_csv('doe2.csv')
