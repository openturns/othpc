# Cantilever beam tutorial

The simple example of the cantilever beam allows us to illustrate how to use the `OpenTURNSWrapper` class. This example is based on a quick numerical model, which was proposed in the documentation of an OpenTURNS module (see https://openturns.github.io/otwrapy/master/beam_wrapper.html).

In this case, the numerical model is an executable that computes the deviation of a beam under bending stress according to the following expression:  
```{math}
y = \frac{FL^3}{3EI}
```
where E is the Young modulus (Pa),
F is the Loading (N),
L is the Length of beam (m)
and I is the Moment of inertia (m^4).

```{image} beam.png
:class: bg-primary
:width: 400px
:align: center
```

To evaluate this numerical model, one can run the following shell command: 
```
$ beam -x beam_input.xml
```
where `beam_input.xml` is the input file containing the four parameter. Note that an example of this file can be created by manually replacing the tokens `@F@, @E@, @L@, @I@` by numerical values in the file `template/beam_input_template.xml`. The output of the code is an xml file `_beam_outputs_.xml` containing the deviation and its derivates.

## 1- Prepare your environment on the cluster

The following commands suit the users who have access to one of the clusters owned by EDF (in the following the cluster is name CRONOS). 
- Connect to CRONOS, create your Python environment called `myenv` using conda-forge:
  ```
  NNI@dspxxxxxxx:~$ ssh cronos
  [NNI-crfront1-pts48] ~ $ module load Miniforge3
  [NNI-crfront1-pts48] ~ $ conda create -n myenv 
  ```
  The creation of your environment (second line), does not need to be repeated at each connection.

- Clone the git repository in your "scratch" space and create your branch:
  ```
  (myenv) [NNI-crfront1-pts48] ~$ cd /scratch/users/{NNI}/
  (myenv) [NNI-crfront1-pts48] ~$ git clone [https://github.com/openturns/othpc](https://github.com/openturns/othpc)
  (myenv) [NNI-crfront1-pts48] ~$ pip install -e othpc/
  ```

## 2- Files required for the cantilever beam  

The requirements for this example include:

- Template input file (here, `template/beam_input_template.xml`);

- Executable file (here, `template/beam`);

- Input design of experiments to be evaluated (here, `input_doe/doe.csv`).

- Output folder for my results (here, `my_results`)

  In the case of the cantilever beam, this is its content:
  ```
  ├── cantilever_beam
  |   ├── input_doe
  |   |    ├── doe.csv 
  |   ├── template
  |   |    ├── beam.exe
  |   |    ├── beam_input_template.xml
  |   ├── my_results 
  ```

## 3- How to run an `othpc` script?


### Define the simulation model

```Python
import othpc
import openturns as ot
from othpc.example import CantileverBeam

my_results_directory = "my_results"
cb = CantileverBeam(my_results_directory, n_cpus=2)
```

Note that the argument `n_cpus` is set here to 2 (by default `n_cpus=1`). 
Therefore, the evaluation of a sample of input points is distributed by `multiprocessing` on 2 CPUs.  

### Define an OpenTURNS function distributing its evaluations

```Python
sf = othpc.SubmitFunction(cb, evals_per_job=2, cpus_per_job=2, timeout_per_job=5)
f = ot.Function(sf)
```
As the evaluations of the `CantileverBeam` class are distributed over 2 CPUs here (see remark above), 
two evaluation are done per SLURM job. 

### Define input design of experiments with size `N=10` and evaluate it on the HPC

```Python
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
Y = f(X)
print(Y)
```

### Create a summary table gathering inputs and corresponding evaluated outputs 

```Python
othpc.make_summary_file("my_results", summary_file="summary_table.csv")
```

## 3- Resulting file tree

After running the previous Python script, one gets the following file-tree results. 
In the folder `my_results`, 10 subfolders have been created with a unique hash, corresponding to each evaluation. 
In the `logs` folder, 5 subfolders were created, corresponding to all the SLURM jobs submitted (since the argument `evals_per_job=2` here).

```
  ├── cantilever_beam
  |   ├── input_doe
  |   |    ├── doe.csv 
  |   ├── template
  |   |    ├── beam.exe
  |   |    ├── beam_input_template.xml
  |   ├── logs
  |   │   ├── 54474902
  |   │   ├── 54474903
  |   │   ├── 54474904
  |   │   ├── 54474906
  |   │   └── 54474907
  |   ├── my_results
  |   │   ├── simu_2025-05-13_17-37_69us6w9c
  |   │   ├── simu_2025-05-13_17-37_71krv2ic
  |   │   ├── simu_2025-05-13_17-37_ejk7pqsl
  |   │   ├── simu_2025-05-13_17-37_p4jyjbp2
  |   │   ├── simu_2025-05-13_17-37_t687ohjt
  |   │   ├── simu_2025-05-13_17-37_xv_pbjmo
  |   │   ├── simu_2025-05-13_17-38_0ueo2xry
  |   │   ├── simu_2025-05-13_17-38_95e6rhvd
  |   │   ├── simu_2025-05-13_17-38_q0czcyr3
  |   │   ├── simu_2025-05-13_17-38_qombpgv0
  |   │   └── summary_table.csv
```
