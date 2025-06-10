[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


# OpenTURNS meets High-Performance Computing


## What is `othpc`?

`othpc` is a simple Python tool that facilitates the evaluation of numerical models on a SLURM based High-Performance Computing (HPC) facility.

The Python package allows to apply the Uncertainty Quantification (UQ) methods from OpenTURNS directly on a computationnaly costly numerical model (e.g., FEM or CFD model) deployed on HPC 

### Minimal example

```Python
import othpc
import openturns as ot

def product_function(X):
    othpc.fake_load(5) # Fake CPU load for 5 sec.
    return [X[0] * X[1]]
ot_product = ot.PythonFunction(2, 1, product_function, n_cpus=2)
othpc_product = othpc.SubmitFunction(ot_product, tasks_per_job=2, cpus_per_job=2, timeout_per_job=5)
distribution = ot.JointDistribution([ot.Uniform(0., 1.), ot.Normal(0., 1.)])
x_sample = distribution.getSample(6) # Monte Carlo sample with size N=6
y_sample = othpc_product(x_sample) # Submits 3 jobs, each including 2 evaluations 
print(y_sample)
```

Corresponding output:
```Shell
100%|██████████████████████████████████████████████████████████████████████| 3/3 [00:10<00:00,  3.42s/it]
     [ y0         ]
 0 : [  0.163549  ]
 1 : [ -0.0823236 ]
 2 : [  0.237238  ]
 3 : [  1.74489   ]
 4 : [  0.0453774 ]
 5 : [ -0.0501733 ]
```

The Python function created here should be replaced by a executable numerical model, see e.g., the CantileverBeam example. 

Working with `othpc` gives access to the OpenTURNS UQ methods.



## :floppy_disk: How to install?

The package has not been deployed on a downloading platform yet, to install the current development: 

```bash
git clone https://github.com/openturns/othpc.git
pip install -e othpc/
``` 


## Documentation

Sphinx documentation : http://openturns.github.io/othpc/main/


## Contributors

Elias Fekhari, Joseph Muré, Julien Schuller, Michaël Baudin, Pascal Borel.
