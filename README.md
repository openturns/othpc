[![License: LGPL v3](https://img.shields.io/badge/License-LGPLv3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)


# OpenTURNS meets High-Performance Computing


## What is `othpc`?

`othpc` is a simple Python tool that facilitates the evaluation of numerical models on a SLURM based High-Performance Computing (HPC) facility.

The Python package allows one to apply the Uncertainty Quantification (UQ) methods from OpenTURNS directly on a computationally costly numerical model (e.g., FEM or CFD model) deployed on HPC.

### Minimal example

Create a separate script defining your function, here is an example for a script named `product_function.py`:

```Python
# product_function.py
import openturns as ot

class ProductFunction(ot.OpenTURNSPythonFunction):
    def __init__(self):
        super().__init__(2, 1)

    def _exec(self, x):
        return [x[0] * x[1]]
```

Write the following launching script:
```Python
import othpc
import openturns as ot 
from product_function import ProductFunction

ot_product = ProductFunction()
othpc_product = othpc.SubmitFunction(ot_product, ntasks_per_node=3, timeout_per_job=5)
distribution = ot.JointDistribution([ot.Uniform(0., 1.), ot.Normal(0., 1.)])
x_sample = distribution.getSample(12) # Monte Carlo sample with size N=12
y_sample = othpc_product(x_sample) # Submits 4 SLURM jobs, each including a batch of 3 evaluations 
print(y_sample)
```

Here is the corresponding output:
```
100%|██████████████████████████████████████████████████████████████████████| 4/4 [00:39<00:00,  9.79s/it]
     [ y0          ]
 0 : [  0.0552903  ]
 1 : [ -0.351668   ]
 2 : [ -0.0928364  ]
 3 : [  0.023483   ]
 4 : [ -0.0724111  ]
 5 : [  0.33814    ]
 6 : [  0.10313    ]
 7 : [  0.332978   ]
 8 : [  0.0561647  ]
 9 : [ -0.00693689 ]
10 : [  0.735135   ]
11 : [  0.107765   ]
```

Beyond this basic example, the `ProductFunction` class is meant to be replaced by the execution of a numerical model. 
The `CantileverBeam` example illustrates the use of an executable in this context, and exploits most of the services provided by `othpc`.  

### Services and utils

Working with `othpc` simplifies the evaluation of costly numerical models and gives access to the OpenTURNS UQ methods.
Among the services possibly provided by the package: 

- Temporary result directory management.
- Cache mechanism to avoid repeating evaluations.
- Compatibility with multi-core or multi-node numerical models.
- Summary csv table presenting the evaluated inputs with their corresponding outputs.



## How to install?

To install the current version:

```bash
pip install othpc
```

or, from conda:

```bash
conda install conda-forge::othpc
```

## Documentation

Package documentation : http://openturns.github.io/othpc/main/



## Contributors

Elias Fekhari, Joseph Muré, Julien Schueller, Michaël Baudin, Pascal Borel.
