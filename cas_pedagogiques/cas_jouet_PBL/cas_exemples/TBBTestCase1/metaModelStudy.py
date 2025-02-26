#!/usr/bin/env python
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=44
#SBATCH --partition=cn
#SBATCH --exclusive
#SBATCH --time=00:30:00
#SBATCH --wckey=P120F:PYTHON
#SBATCH --output=job_%j.out.log
#SBATCH --error=job_%j.err.log

import openturns as ot
import math

# class funcExec(ot.OpenTURNSPythonFunction):

inputDimension = 40
outputDimension = 1


def _exec(X):
    dimension = len(X)
    if sum(X) > 0:
        Y = math.sqrt(sum(X))
    else:
        Y = 0
    return [Y]


ot_exec = ot.PythonFunction(inputDimension, outputDimension, _exec)

# define large dimension mutlivariate dimension
distribution = ot.Uniform(-1, 10)
composedDistribution = ot.ComposedDistribution([distribution] * inputDimension)

experiment = ot.MonteCarloExperiment(composedDistribution, 3000)

xdata = experiment.generate()
ydata = ot_exec(xdata)

covarianceModel = ot.SquaredExponential([0.1] * inputDimension, [1.0])
basis = ot.ConstantBasisFactory(inputDimension).build()

#algo = ot.KrigingAlgorithm(xdata, ydata, covarianceModel, basis)
# algo.run()


def compute_sparse_least_squares_chaos(
    inputTrain, outputTrain, basis, totalDegree, distribution
):
    """
    Create a sparse polynomial chaos based on least squares.

    * Uses the enumerate rule in basis.
    * Uses the LeastSquaresStrategy to compute the coefficients based on
      least squares.
    * Uses LeastSquaresMetaModelSelectionFactory to use the LARS selection method.
    * Uses FixedStrategy in order to keep all the coefficients that the
      LARS method selected.

    Parameters
    ----------
    inputTrain : Sample
        The input design of experiments.
    outputTrain : Sample
        The output design of experiments.
    basis : Basis
        The multivariate chaos basis.
    totalDegree : int
        The total degree of the chaos polynomial.
    distribution : Distribution.
        The distribution of the input variable.

    Returns
    -------
    result : PolynomialChaosResult
        The estimated polynomial chaos.
    """
    selectionAlgorithm = ot.LeastSquaresMetaModelSelectionFactory()
    projectionStrategy = ot.LeastSquaresStrategy(
        inputTrain, outputTrain, selectionAlgorithm
    )
    enumerateFunction = basis.getEnumerateFunction()
    basisSize = enumerateFunction.getBasisSizeFromTotalDegree(totalDegree)
    adaptiveStrategy = ot.FixedStrategy(basis, basisSize)
    chaosAlgo = ot.FunctionalChaosAlgorithm(
        inputTrain, outputTrain, distribution, adaptiveStrategy, projectionStrategy
    )
    chaosAlgo.run()
    result = chaosAlgo.getResult()
    return result


basis = ot.OrthogonalProductPolynomialFactory(
    [composedDistribution.getMarginal(i) for i in range(inputDimension)]
)
totalDegree = 5  # Polynomial degree
result = compute_sparse_least_squares_chaos(
    xdata, ydata, basis, totalDegree, composedDistribution
)
result
