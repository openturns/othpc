import othpc
import openturns as ot
import openturns.testing as ott
from othpc.example import warren_truss_displacement  
import pytest


@pytest.fixture
def model():
    truss_model = ot.PythonFunction(3, 1, warren_truss_displacement)
    sf = othpc.SubmitFunction(truss_model, evals_per_job=2, cpus_per_job=2, timeout_per_job=5)
    f = ot.Function(sf)
    return f


def test_sample(model):
    X = [[2.22028e+11, 0.0103039, -2094.11],
         [1.84165e+11, 0.00960417, -1947.8],
         [2.00019e+11, 0.0114843, -2458.01],
         [2.35658e+11, 0.0107884, -2256.58],
         [1.68096e+11, 0.0107696, -2262.36]]
    Y = model(X)
    Y_ref = [[-3.00491e-05],
             [-3.6151e-05],
             [-3.51279e-05],
             [-2.91375e-05],
             [-4.10248e-05]]
    ott.assert_almost_equal(Y, ot.Sample(Y_ref))
