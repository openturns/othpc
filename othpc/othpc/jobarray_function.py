#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""
import os
import time
import othpc
import pickle
import inspect
import openturns as ot
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
        slurm_extra_options=["--output=logs/output.log", "--error=logs/error.log"],
        verbose=False,
    ):
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self.job_number = job_number
        self.nodes_per_job = nodes_per_job
        self.cpus_per_job = cpus_per_job
        self.timeout_per_job = timeout_per_job
        self.memory_per_job = memory_per_job
        self.slurm_extra_options = slurm_extra_options
        self.slurm_wckey = slurm_wckey
        #
        self.class_name = type(callable).__name__
        self.callable = callable
        self.callable_file = inspect.getfile(type(callable))
        
        if verbose:
            print(
                "** Requested ressources **\n"
                "**************************\n"
                f"+ job_number--------{self.job_number}\n"
                f"+ cpus_per_job------{self.cpus_per_job}\n"
                f"+ timeout_per_job---{self.timeout_per_job} minutes\n"
                f"+ memory_per_job----{self.memory_per_job} MB\n"
            )   
        # print(self.callable_file)

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
"""
                # Write the job_launcher
                with open(job_launcher_path, "w") as file:
                    file.write(job_launcher_string)
            # Create job-array script
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
"""
            for slurm_extra_option in self.slurm_extra_options: 
                sbatch_string +=f"""
#SBATCH {slurm_extra_option}"""
            sbatch_string +="""
python job_launcher_$SLURM_ARRAY_TASK_ID.py
"""
            # Write the sbatch file
            with open(sbatch_file_path, "w") as file:
                file.write(sbatch_string)
            otct.execute(f"sbatch {sbatch_file_path}", cwd=tmp_dir, capture_output=True)
            # Wait until jobs are finished
            remaining_jobs = len(X)
            while remaining_jobs > 0:
                time.sleep(10)
                df = othpc.utils.get_slurm_jobs()
                remaining_jobs = df.shape[0]
            # Parse the outputs
            for i in range(len(X)):
                output_path = os.path.join(tmp_dir, f"ysample_{i}.csv")
                try:
                    output = ot.Sample.ImportFromCSVFile(output_path)
                except:
                    output = ot.Sample(1, self.getOutputDimension())
                    output[0, 0] = float("nan")
                outputs.add(output)
        return outputs


# TODO: 
# Allow to have batches instead of the current 1 job per evaluation 