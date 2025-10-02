import othpc
import openturns as ot
import openturns.testing as ott
from othpc.example import MPILoadSimulator
import pytest


@pytest.fixture
def model():
    cb = MPILoadSimulator(nb_mpi_proc=10, nb_slurm_nodes=2, simu_duration=2)
    sf = othpc.SubmitFunction(cb, timeout_per_job=10)
    f = ot.Function(sf)
    return f


# @pytest.mark.skip(reason="cluster is too busy")
def test_sample(model):
    X = [
        [2.5975311321555417e00, 2.6138941107696212e-02],
        [7.6561044743852058e00, 2.8803937992536532e-01],
        [7.2944729836231792e00, 8.2344094806084591e00],
        [9.3499449759123046e00, 4.4022912406636117e00],
        [3.0588591757295625e00, 1.7400261723379415e00],
        [9.3884604226997865e00, 6.4923386545128352e00],
        [8.4135918671410117e00, 4.2430163412984925e00],
        [6.0803028987646002e-02, 7.0259545068090512e00],
        [8.7358784697389922e00, 6.4811437693300391e00],
        [4.1448621250453677e00, 1.1972157708374951e00],
    ]
    Y = model(X)
    Y_ref = [
        [1.6197746983032046],
        [2.818535764241882],
        [3.9406703064620414],
        [3.7084007626706037],
        [2.1906358319144474],
        [3.9850720291122244],
        [3.5576127119796928],
        [2.6620964550137356],
        [3.9009001831717036],
        [2.311293554675144],
    ]

    ott.assert_almost_equal(Y, Y_ref)
