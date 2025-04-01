# `othpc` package to evaluate simulation models on high performance computers

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

General repository of the `othpc` Python package.


## What is `othpc`?

The Python package `othpc` offers a standardized development framework to control the evaluations of any numerical model distributed on a cluster orchestrated by SLURM from a Python script. 
In addition, the architecture of the package allows the user to retreive an OpenTURNS Function, wrapping its distributed numerical model. 
This way, the user can directly access all the services in OpenTURNS (package dedicated to uncertainty quantification) and easily conduct his uncertainty quantification studies on a computationnaly costly numerical model. 


## Who is `othpc` for?



## :floppy_disk: How to install `othpc`?

The package has not been deployed on a downloading platform yet, to install the current development: 

```bash
pip install -e .
``` 