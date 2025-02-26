"""
Lance une étude paramétrique du cas de la poutre encastrée avec SLURM/jobarray

Exemple
-------
$ python runParametricBeam.py
"""
import shutil
import numpy as np
import os.path as osp
import os
import re
import subprocess
import openturns as ot
import openturns.coupling_tools as otct

# Create the main working directory: this is different for each parametric study
masterDir = "/scratch/users/C61372/beam"
workDir = osp.join(masterDir, "work")
os.mkdir(workDir)

print("1. Set the probabilistic model")

# Young's modulus E
E = ot.Beta(0.9, 3.5, 65.0e9, 75.0e9)  # in N/m^2
E.setDescription("E")
E.setName("Young modulus")

# Load F
F = ot.LogNormal()  # in N
F.setParameter(ot.LogNormalMuSigma()([300.0, 30.0, 0.0]))
F.setDescription("F")
F.setName("Load")

# Length L
L = ot.Uniform(2.5, 2.6)  # in m
L.setDescription("L")
L.setName("Length")

# Moment of inertia I
II = ot.Beta(2.5, 4.0, 1.3e-7, 1.7e-7)  # in m^4
II.setDescription("I")
II.setName("Inertia")

# correlation matrix
R = ot.CorrelationMatrix(4)
R[2, 3] = -0.2
copula = ot.NormalCopula(
    ot.NormalCopula.GetCorrelationFromSpearmanCorrelation(R)
)
distribution = ot.ComposedDistribution([E, F, L, II], copula)

input_template = "beam_input_template.xml"
actual_beam_file = "beam.xml"

print("2. Generate the design of experiments")

sample_size = 10
input_sample = distribution.getSample(sample_size)

print("Création de tous les répertoires d'où vont être lancés les jobs")
for i in range(sample_size):
    jobindex = i + 1
    print(f"Création répertoire #{jobindex} / {sample_size}")
    curDir = osp.join(workDir, "{}".format(jobindex))  # tasks are 1-based
    print(f"Create {curDir}")
    os.mkdir(curDir)

    # From the template file, create the actual input file
    current_point = input_sample[i]
    print(f"Create {actual_beam_file}")
    otct.replace(
        input_template, actual_beam_file, ["@F", "@E", "@L", "@I"], current_point
    )

    # copie fichiers into the current job directory
    print(f"Copy beam into {curDir}")
    shutil.copy("beam", curDir)
    print(f"Copy {actual_beam_file} into {curDir}")
    shutil.copy(actual_beam_file, curDir)

# Go in the working directory
os.chdir(workDir)

# Write the input design of experiments
input_filename = osp.join(workDir, "input.csv")
print(f"Write input data into {input_filename}")
input_sample.exportToCSVFile(input_filename)

# Write SBATCH script
sh_file = f"""#!/bin/bash
#SBATCH --job-name=myJobarrayTest
#SBATCH --nodes=1 --ntasks=1
#SBATCH --time=4:00:00
#SBATCH --output=test_%A_%a.out
#SBATCH --error=test_%A_%a.err
#SBATCH --partition=cn
#SBATCH --array=1-{sample_size}
#SBATCH --wckey=P11YB:ASTER

cd /scratch/users/C61372/beam/work/$SLURM_ARRAY_TASK_ID
./beam -x beam.xml
"""

full_bash_filename = osp.join(workDir, "lance_jobs.sh")
print(f"Write the jobarray/SLURM bash script {full_bash_filename}")
with open(full_bash_filename, "w") as file:
    file.write(sh_file)

# subprocess.Popen(['sbatch', 'lance_jobs.sh'])

