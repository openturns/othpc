import math
import os
import othpc
import openturns as ot
import openturns.testing as ott
from othpc.example import CantileverBeam
import pandas as pd
import pytest
import shutil


@pytest.fixture
def model():
    # output file precision is limited in _beam_output.xml so increase fd step to avoid null gradient
    ot.ResourceMap.SetAsScalar("CenteredFiniteDifferenceGradient-DefaultEpsilon", 1e-3)
    my_results_directory = "my_results"
    shutil.rmtree(my_results_directory, ignore_errors=True)
    cb = CantileverBeam(my_results_directory, n_cpus=1, fake_load_time=1)
    sf = othpc.SubmitFunction(cb, ntasks_per_node=2, cpus_per_task=1, timeout_per_job=5)
    f = ot.Function(sf)
    return f


def test_point(model):
    x = [31725.5, 32427091.2, 256.37, 408.25]
    y = model(x)
    ott.assert_almost_equal(y, [13.4603])


def test_gradient(model):
    x = [31725.5, 32427091.2, 256.37, 408.25]
    y = model.gradient(x)
    othpc.make_summary_file("my_results", summary_file="summary_table.csv")
    ott.assert_almost_equal(y, ot.Matrix([[0.0], [0.0], [0.155], [-0.035]]))


def test_failure(model):
    x = [-1] * 4
    y = model(x)
    assert math.isnan(y[0])
    othpc.make_summary_file("my_results", summary_file="summary_table.csv")
    table = pd.read_csv(os.path.join("my_results", "summary_table.csv"))
    resdir = table.iloc[0, 0]
    assert os.path.exists(resdir)
    with open(os.path.join(resdir, "CantileverBeam_RuntimeError.txt"), "r") as f:
        lines = f.readlines()
    assert "F est strictement negatif" in lines[1]


def test_sample(model):
    X = [
        [33021.47, 28315077.8, 253.31, 397.93],
        [18837.04, 34918130.37, 253.61, 403.45],
        [18612.64, 28268628.1, 250.95, 367.27],
        [37342.44, 32361697.82, 252.88, 377.74],
        [30384.71, 35487053.16, 251.5, 346.03],
        [31725.5, 32427091.2, 256.37, 408.25],
        [28373.01, 29795978.07, 252.35, 359.77],
        [19772.44, 35220107.98, 259.14, 381.86],
        [34404.52, 32819268.93, 257.05, 367.13],
        [35162.69, 37735224.37, 253.19, 0.0],
    ]
    Y = model(X)
    print(Y)
    assert len(Y) == len(X)
    Y_ref = [
        [15.8784],
        [7.27026],
        [9.44405],
        [16.4665],
        [13.1209],
        [13.4603],
        [14.1779],
        [8.52801],
        [16.1658],
    ]
    ott.assert_almost_equal(Y[:9], ot.Sample(Y_ref[:9]))
    assert Y[9, 0] == float("inf")
    othpc.make_summary_file("my_results", summary_file="summary_table.csv")
    summary_file = os.path.join("my_results", "summary_table.csv")
    table = pd.read_csv(summary_file)
    assert table.shape == (
        len(X),
        1 + model.getInputDimension() + model.getOutputDimension(),
    )

    # test reload from cache
    memoize = othpc.load_cache(model, summary_file)
    Y = memoize(X)
    ott.assert_almost_equal(Y[:9], ot.Sample(Y_ref[:9]))
    table = pd.read_csv(summary_file)
    assert table.shape == (
        len(X),
        1 + model.getInputDimension() + model.getOutputDimension(),
    )
