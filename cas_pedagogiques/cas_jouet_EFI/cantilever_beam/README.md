# Using HPC for Uncertainty Quantification and parametric studies

This guide offers solutions to deploy a computationally costly numerical model (i.e., an input-output executable model) on a high-performance computing (HPC) facility.

## Who is it for?

- Anyone who has access to a SLURM-orchestrated HPC facility but is not a SLURM expert, and wishes to launch and manage his HPC evaluations from a single Python script.

- Anyone who needs to evaluate a costly numerical model on a given input design of experiments (i.e., for parametric studies of the numerical model or to build a surrogate model).

- Anyone who wishes to directly plug his numerical model to the numerous methods from OpenTURNS, a Python library dedicated to Uncertainty Quantification (e.g., for reliability analysis, optimization, active learning).

## How to use this guide? - *Illustration on the Cantilever beam example*

The simple example of the cantilever beam allows us to illustrate how to use the `OpenTURNSWrapper` class. This example is based on a quick numerical model, which was proposed in the documentation of an OpenTURNS module (see https://openturns.github.io/otwrapy/master/beam_wrapper.html).


In this case, the numerical model is an executable that computes the deviation of a beam under bending stress according to the following expression:  
$$
y = \frac{FL^3}{3EI} ,
$$
where E is the Young modulus (Pa),
F is the Loading (N),
L is the Length of beam (m)
and I is the Moment of inertia (m^4).

<p align="center">
  <img src=beam.png width="20%" />
</p>


To evaluate this numerical model, one can run the following shell command: 
```
$ beam -x beam_input.xml
```
where `beam_input.xml` is the input file containing the four parameter. Note that an example of this file can be created by manually replacing the tokens `@F@, @E@, @L@, @I@` by numerical values in the file `template/beam_input_template.xml`. The output of the code is an xml file `_beam_outputs_.xml` containing the deviation and its derivates.

### 1- Prepare your environment in CRONOS

- Connect to CRONOS, create your Python environment called `myenv` using conda-forge:
  ```
  NNI@dspxxxxxxx:~$ ssh cronos
  [NNI-crfront1-pts48] ~ $ module load Miniforge3
  [NNI-crfront1-pts48] ~ $ conda create -n myenv openturns dask-jobqueue 
  [NNI-crfront1-pts48] ~ $ conda activate myenv
  ```
  The creation of your environment (second line), does not need to be repeated at each connection.

- Clone the git repository in your "scratch" space and create your branch:
  ```
  (myenv) [NNI-crfront1-pts48] ~ $ cd /scratch/users/NNI/
  (myenv) [NNI-crfront1-pts48] /scratch/users/NNI/ $ git clone https://gitlab.pleiade.edf.fr/projet-incertitudes/openturns/openturns/actions-openturns/hpc.git
  (myenv) [NNI-crfront1-pts48] /scratch/users/NNI/ $ cd hpc/
  (myenv) [NNI-crfront1-pts48] /scratch/users/NNI/hpc/ $ git checkout -b mybranch
  ```

### 2- Define your template folder

It should include:

- Template input file (here, `template/beam_input_template.xml`);

- Executable file (here, `template/beam`);

- Input design of experiments to be evaluated (here, `input_doe/doe.csv`).

In the case of the cantilever beam, this is its content:
  ```
    ├── cantilever_beam
    |   ├── input_doe
    |   |    ├── doe.csv 
    |   ├── template
    |   |    ├── beam.exe
    |   |    ├── beam_input_template.xml
  ```

### 3- Pick one framework to launch your parallel evaluations


A short description of the frameworks is proposed below. By default, one can start with the native framework from SLURM included in the `SLURMJobArrayWrapper` class. To familiarize with the three alternatives, small tests can be performed on the demo files named `demo_jobarray.sh`, `demo_glost.sh`, `demo_dask.py`.

- **SLURM JobArray:** A simple `for` loop with a SLURM syntax, launching one single job per evaluation of the numerical model (see e.g., https://osirim.irit.fr/docs/slurm/job-array/).
  
  - Class name: `SLURMJobArrayWrapper`
  - ++ Simple and native SLURM framework, is well suited to parallel codes.
  - -- Can easily reach HPC quotas regarding the number of simultaneous jobs. In the case of the CRONOS cluster, this quota is at 500 simultaneous jobs. Unreachable job status from the Python environment.  

- **Glost:** This C++ based module allows to gather a list of independent shell tasks into a single job. Glost stands for "Greedy Launcher Of Small Tasks" and is developed by the CEA (see https://github.com/cea-hpc/glost/tree/master).
  - Class name: `GlostWrapper`
  - ++ Well suited for sequential codes that need to be evaluated many times (typically more times than the quota on simultaneous jobs).  On CRONOS, this Unix module can loaded easily since it is already installed by the IT service.
  - -- This framework is not adapted to parallel codes since it already uses mpi. Unreachable job status from the Python environment.

- **Dask:** This framework relies on an important Python package with an API fully proposed in Python (see https://jobqueue.dask.org/en/latest/index.html).
  - Class name: `DaskWrapper`
  - ++ It offers many services, including for example access to the jobs' statues.
  - -- This option requires the installation of the Python package (available on conda and pip platforms).



### 4- Adapt the wrapper to your numerical model

This section describes the files to be modified to fit your numerical code. Most of the changes are done on the base class `OpenTURNSWrapper`.

- Input template file(s)
  - Adapt the method `OpenTURNSWrapper._build_subtree` by changing the input variables.
  - Replace the input template file `template/beam_input_template.xml` by your input file and introduce input tokens.

- Output file(s)
  - Adapt the method `OpenTURNSWrapper._parse_outputs` by retrieving your output of interest for each evaluation of the wrapper.
  
- Execution commands
  - For the `SLURMJobArrayWrapper` class: adapt the `jobarray_launcher.sh` file.
  - For the `GlostWrapper` class: adapt the `glost_launcher.sh` file.
 
  - For the `DaskWrapper` class: adapt the `DaskWrapper._execute()` method.

- Required SLURM resources
  - Adapt the resources by editing the Python dictionary `OpenTURNSWrapper.slurm_resources`, for example:
    ```python
    #!/usr/bin/env python3
    import openturns as ot
    from wrapper_jobarray import SLURMJobArrayWrapper

    X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
    my_wrapper = SLURMJobArrayWrapper(input_dimension=X.getDimension(), output_dimension=1, index_col=0)
    my_wrapper.slurm_resources = {
    "nodes-per-job": 1,
    "cpus-per-job": 4,
    "mem-per-job": 1024, # 1024 MB
    "timeout": "00:30:00", # 30 minutes
    "nb-jobs": 4
    }
    ```

### 5- Launch your wrapper on CRONOS

The following Python script, named `evaluate_doe.py`, defines an OpenTURNS function wrapping the cantilever beam executable that is used to evaluate a design of experiments:
```python
#!/usr/bin/env python3
import openturns as ot
from wrapper_jobarray import SLURMJobArrayWrapper

X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
my_wrapper = SLURMJobArrayWrapper(input_dimension=X.getDimension(), output_dimension=1, index_col=0)
g = my_wrapper.get_function()
Y = g(X)
XY = my_wrapper.make_inputoutput_file(g, X)
```

To execute the Python script on CRONOS:
  - **Default launch**: if the CRONOS terminal is disconnected, the Python process!
    ```
    (myenv) [NNI-crfront1-pts48] /scratch/users/NNI/hpc/../cantilever_beam $ python evaluate_doe.py &
    ```
  - **Nohup launch**: even if the CRONOS terminal is disconnected, the Python process keeps running on one specific front node (here `crfront1`).
    ```
    (myenv) [NNI-crfront1-pts48] /scratch/users/NNI/hpc/../cantilever_beam $ nohup python -u evaluate_doe.py input_doe/doe.csv 2>&1 &
    ```
    One can manually kill this process if needed by running the following commands:
    ```
    (myenv) [NNI-crfront1-pts48] /scratch/users/NNI/hpc/../cantilever_beam $ ps -ef | grep evaluate_doe.py
      process number: #xxxxx
    (myenv) [NNI-crfront1-pts48] /scratch/users/NNI/hpc/../cantilever_beam $ pkill #xxxxx
    ```

The results from this evaluation are stored in two ways:
  - Result directories (indexes here according to the column `index_col=0` of `input_doe/doe.csv`), and summary `inout_results.csv` table:
    ```
      ├── cantilever_beam
      |   ├── input_doe
      |   |    ├── doe.csv
      |   ├── template
      |   ├── results_#timestamp
      |   |    ├── inout_results.csv
      |   |    ├── SIMU_0
      |   |    |    ├── beam_input.xml
      |   |    |    ├── _beam_output_.xml      
      |   |    ├── SIMU_3
      |   |    ├── ...
    ```
  - `OpenTURNS.MemoizeFunction` storing all the evaluations of the wrapper as a pickle file:
    ```python
    #!/usr/bin/env python3
    import openturns as ot
    from wrapper_jobarray import SLURMJobArrayWrapper

    X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
    my_wrapper = SLURMJobArrayWrapper(input_dimension=X.getDimension(), output_dimension=1, index_col=0)
    g = my_wrapper.get_function()
    Y = g(X)
    XY = my_wrapper.make_inputoutput_file(g, X)
    with open("beam_evals.pkl", "wb") as ot_study:
        pickle.dump(g, ot_study)
    ```
    One can also load previous evaluations of this wrapper using the argument `previous_evals_file` from the method `get_function()`. This avoids repeating twice the same evaluation, see e.g.,:
    ```python
    #!/usr/bin/env python3
    import openturns as ot
    from wrapper_jobarray import SLURMJobArrayWrapper

    X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
    my_wrapper = SLURMJobArrayWrapper(input_dimension=X.getDimension(), output_dimension=1, index_col=0)
    g = my_wrapper.get_function(previous_evals_file="beam_evals.pkl")
    Y = g(X)
    XY = my_wrapper.make_inputoutput_file(g, X)
    with open("beam_evals.pkl", "wb") as ot_study:
        pickle.dump(g, ot_study)
    ```


### Future developments

- The code currently returns `nan` values in case of crash (e.g., using a `FileNotFoundError` Python exception). This feature should be further tested.
- Adapt the resources for a same wrapper. Cf. the remark of Pascal Borel.
- How to manage restarts? Maybe have a status 

# Dashboard DASK : comment l'utiliser

Le problème de l'utilisation du tableau de bord DASK est que l'URL correspond au cluster et n'est pas accessible depuis une machine locale. La solution est un tunnel SSH. Dans la commange qui suit, on suppose que l'adresse du Dashboard obtenue via `cluster.dashboard_link` est  `http://A.B.C.D:8787/status` où A.B.C.D. est l'adresse IP de la frontale utilisée, et aussi que la commande ssh nous dirige vers la même frontale :

```shell
ssh -L 8001:localhost:8787 cronos
```

Il est ensuite possible de se connecter au tableau de bord en tapant l'URL suivante dans la barre du navigateur :

```
localhost:8081
```

Il est possible que cette technique permette de disposer sur une machine locale d'un client d'un SLURMCluster, via la commande

```python
from distributed.client import Client
c = Client(address="localhost:8001)
```
où 8001 écouterait non pas le port du Dasboard, mais directement celui du SLURMCluster vivant sur Cronos.
