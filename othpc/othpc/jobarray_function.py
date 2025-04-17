#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""
import os
import time
import othpc
import datetime
import openturns as ot
import subprocess
from io import StringIO
import csv


from simple_slurm import Slurm
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

    def _exec_sample(self, X):
        X = ot.Sample(X)

        outputs = ot.Sample(0, self.getOutputDimension())
        with othpc.TempSimuDir(res_dir=".", prefix="tmp_", cleanup=False) as tmp_dir:
            tmp_dir = os.path.abspath(tmp_dir)
            print("Path repo temporaire", tmp_dir)
            # Create model in the simulation directory
            study_path = os.path.join(tmp_dir, "user_function.xml")
            study = ot.Study()
            study.setStorageManager(ot.XMLStorageManager(study_path))
            study.add("user_function", ot.Function(self.callable))
            study.save()

            # Create job_launchers
            for i, x in enumerate(X):
                input_path = os.path.join(tmp_dir, f"xsample_{i}.csv")
                output_path = os.path.join(tmp_dir, f"ysample_{i}.csv")
                job_launcher_path = os.path.join(tmp_dir, f"job_launcher_{i}.py")
                ot.Sample.BuildFromPoint(x).exportToCSVFile(input_path)
                job_launcher_string = f"""import openturns as ot
study = ot.Study()
study.setStorageManager(ot.XMLStorageManager("{study_path}"))
study.load()
user_function = ot.Function()
study.fillObject("user_function", user_function)
x = ot.Sample.ImportFromCSVFile("{input_path}")
y = user_function(x)
y.exportToCSVFile("{output_path}")
"""
                # Write the job_launcher
                with open(job_launcher_path, "w") as file:
                    file.write(job_launcher_string)

            slurm = Slurm(
                array=range(len(X)),
                nodes=self.nodes_per_job,
                cpus_per_task=self.cpus_per_job,
                mem=self.memory_per_job,
                job_name=self.class_name,
                output=f"logs/{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out",
                time=datetime.timedelta(minutes=self.timeout_per_job),
                wckey=self.slurm_wckey,
            )
            # slurm.add_cmd(f"#SBATCH {extra_option}")
            slurm.sbatch("python job_launcher_$SLURM_ARRAY_TASK_ID.py", convert=False)
            # Wait until finished

            remaining_jobs = len(X)
            while remaining_jobs > 0:
                time.sleep(10)

                result = subprocess.run(
                    [slurm.squeue.command, "--me", "-o", slurm.squeue.output_format],
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
                # slurm.squeue.update_squeue()
                # jobs = slurm.squeue.jobs
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
