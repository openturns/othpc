import othpc
import openturns as ot
import openturns.testing as ott
from othpc.example import MPILoadSimulator
import pytest


@pytest.fixture
def model():
    cb = MPILoadSimulator(nb_mpi_proc=10, nb_slurm_nodes=2, simu_duration=2)
    sf = othpc.SubmitFunction(cb, evals_per_jobs=1, cpus_per_job=1, timeout_per_job=10)
    f = ot.Function(sf)
    return f


@pytest.mark.skip(reason="cluster is too busy")
def test_sample(model):
    X = [[2.5975311321555417e+00, 2.6138941107696212e-02],
         [7.6561044743852058e+00, 2.8803937992536532e-01],
         [7.2944729836231792e+00, 8.2344094806084591e+00],
         [9.3499449759123046e+00, 4.4022912406636117e+00],
         [3.0588591757295625e+00, 1.7400261723379415e+00],
         [9.3884604226997865e+00, 6.4923386545128352e+00],
         [8.4135918671410117e+00, 4.2430163412984925e+00],
         [6.0803028987646002e-02, 7.0259545068090512e+00],
         [8.7358784697389922e+00, 6.4811437693300391e+00],
         [4.1448621250453677e+00, 1.1972157708374951e+00]]
    Y = model(X)
    Y_ref = [] # TODO 
    ott.assert_almost_equal(Y, ot.Sample(Y_ref))
