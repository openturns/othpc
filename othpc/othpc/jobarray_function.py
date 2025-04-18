#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""
import os
import time
import othpc
import openturns as ot
import subprocess
from io import StringIO
import csv
import pickle
import inspect


import openturns.coupling_tools as otct


class JobArrayFunction(ot.OpenTURNSPythonFunction):
    """
    TBD
    """

    def __init__(
        self,
        callable,
        job_number=1,
        nodes_per_job=1,
        cpus_per_job=4,
        timeout_per_job=5,
        memory_per_job=512,
        slurm_wckey="P120K:SALOME",
        # slurm_extra_options=["--output=logs/output.log", "--error=logs/error.log"],
        # verbose=False,
    ):
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self.job_number = job_number
        self.nodes_per_job = nodes_per_job
        self.cpus_per_job = cpus_per_job
        self.timeout_per_job = timeout_per_job
        self.memory_per_job = memory_per_job
        # self.slurm_extra_options = slurm_extra_options
        self.slurm_wckey = slurm_wckey
        #
        self.class_name = type(callable).__name__
        self.callable = callable
        self.callable_file = inspect.getfile(type(callable))
        print(self.callable_file)

    def _exec_sample(self, X):
        X = ot.Sample(X)

        outputs = ot.Sample(0, self.getOutputDimension())
        with othpc.TempSimuDir(
            res_dir=".", prefix="tmp_", cleanup=False, to_be_copied=[self.callable_file]
        ) as tmp_dir:
            tmp_dir = os.path.abspath(tmp_dir)
            print("Path repo temporaire", tmp_dir)
            # Create model in the simulation directory
            study_path = os.path.join(tmp_dir, "study.pkl")
            with open(study_path, "wb") as f:
                pickle.dump(self.callable, f)
            # study = ot.Study()
            # study.setStorageManager(ot.XMLStorageManager(study_path))
            # study.add("user_function", ot.Function(self.callable))
            # study.save()

            # Create job_launchers
            for i, x in enumerate(X):
                input_path = os.path.join(tmp_dir, f"xsample_{i}.csv")
                output_path = os.path.join(tmp_dir, f"ysample_{i}.csv")
                job_launcher_path = os.path.join(tmp_dir, f"job_launcher_{i}.py")
                sbatch_file_path = os.path.join(tmp_dir, "sbatch_launcher.sh")
                ot.Sample([x]).exportToCSVFile(input_path)
                job_launcher_string = f"""import openturns as ot
import time
import pickle
import os
with open("{study_path}", "rb") as f:
    user_function = pickle.load(f)
x = ot.Sample.ImportFromCSVFile("{input_path}")
y = user_function(x)
ot.Sample(y).exportToCSVFile("{output_path}")
time.sleep(30)
"""
                # Write the job_launcher
                with open(job_launcher_path, "w") as file:
                    file.write(job_launcher_string)

            sbatch_string = f"""#!/bin/sh
#SBATCH --array               0-{len(X)-1}
#SBATCH --cpus-per-task       {self.cpus_per_job}
#SBATCH --job-name            {self.class_name}
#SBATCH --mem                 {self.memory_per_job}
#SBATCH --nodes               {self.nodes_per_job}
#SBATCH --output              logs/output_%a.log
#SBATCH --error               logs/error_%a.log
#SBATCH --time                0-{self.timeout_per_job}
#SBATCH --wckey               {self.slurm_wckey}

python job_launcher_$SLURM_ARRAY_TASK_ID.py
"""
            # Write the sbatch file
            with open(sbatch_file_path, "w") as file:
                file.write(sbatch_string)

            otct.execute(f"sbatch {sbatch_file_path}", cwd=tmp_dir, capture_output=True)

            remaining_jobs = len(X)
            while remaining_jobs > 0:
                time.sleep(10)

                result = subprocess.run(
                    [
                        "squeue",
                        "--me",
                        "-o",
                        "'%i','%j','%t','%M','%L','%D','%C','%m','%b'','%R'",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if result.returncode != 0:
                    raise RuntimeError(f"Error running squeue: {result.stderr}")

                csv_file = StringIO(result.stdout.strip())
                reader = csv.DictReader(
                    csv_file, delimiter=",", quotechar='"', skipinitialspace=True
                )
                jobs = {}
                for num, row in enumerate(reader):
                    # jobs[int(row["JOBID"])] = row
                    jobs[num] = row
                print(jobs)
                remaining_jobs = len(jobs)

            for i in range(len(X)):
                output_path = os.path.join(tmp_dir, f"ysample_{i}.csv")
                try:
                    output = ot.Sample.ImportFromCSVFile(output_path)
                except:
                    output = ot.Sample(1, self.getOutputDimension())
                    output[0, 0] = float("nan")
                outputs.add(output)
        return outputs
