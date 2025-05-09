# Cantilever beam tutorial

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

## 1- Prepare your environment in CRONOS

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
  (myenv) [NNI-crfront1-pts48] ~$ cd /scratch/users/{NNI}/
  (myenv) [NNI-crfront1-pts48] ~$ git clone /https://gitlab.pleiade.edf.fr/projet-incertitudes/openturns/openturns/actions-openturns/hpc-phimeca.git
  (myenv) [NNI-crfront1-pts48] ~$ cd /scratch/users/{NNI}/hpc-phimeca/othpc/
  (myenv) [NNI-crfront1-pts48] ~$ pip install -e .
  ```
  
## 2- Files required for the cantilever beam  

The requirements for this example include:

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

 ## 3- How to use `othpc`?
