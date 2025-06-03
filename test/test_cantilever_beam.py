import os
import othpc
import openturns as ot
from othpc.example import CantileverBeam
import pytest


@pytest.fixture
def model():
    my_results_directory = "my_results"
    try:
        os.mkdir(my_results_directory)
    except FileExistsError:
        pass
    cb = CantileverBeam(my_results_directory, n_cpus=2)
    sf = othpc.SubmitItFunction(cb, tasks_per_job=2, cpus_per_job=2, timeout_per_job=5)
    f = ot.Function(sf)
    return f


def test_point(model):
    x = [31725.5,32427091.2,256.37,408.25]
    y = model(x)
    assert abs(y[0] - 13.4603) < 1e-4


def test_sample(model):
    dw = othpc.SubmitItFunction(model, tasks_per_job=2, cpus_per_job=2, timeout_per_job=5)
    dwfun = ot.Function(dw)
    othpc.make_summary_file("my_results", summary_file="summary_table.csv")
    X = [[-2.0,28315077.8,253.31,397.93],
         [18837.04,34918130.37,253.61,403.45],
         [35162.69,37735224.37,253.19,0.],
         [18612.64,28268628.1,250.95,367.27],
         [37342.44,32361697.82,252.88,377.74],
         [30384.71,35487053.16,251.5,346.03],
         [31725.5,32427091.2,256.37,408.25],
         [28373.01,29795978.07,252.35,359.77],
         [19772.44,35220107.98,259.14,381.86],
         [34404.52,32819268.93,257.05,367.13]]
    Y = dwfun(X)
    print(Y)
    assert len(Y) == len(X)
    othpc.make_summary_file("my_resulsts", summary_file="summary_table.csv")
