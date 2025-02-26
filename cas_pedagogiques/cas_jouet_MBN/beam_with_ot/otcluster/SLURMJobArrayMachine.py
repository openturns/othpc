#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""

import os
import openturns as ot
import shutil
import openturns.coupling_tools as otct
import math
from datetime import datetime
from .WcKeyChecker import WcKeyChecker


class SLURMJobArrayJob:
    def __init__(
        self,
        results_directory,
        simulation_directory_list,
        local_input_sample_csv_filename,
        local_output_sample_csv_filename,
        sample_size,
        block_size,
        input_dimension,
        output_dimension,
        input_description,
        output_description,
    ):
        """
        Create a SLURM JobArray job.

        Parameters
        ----------
        results_directory : str
            The name of the working directory.
        simulation_directory_list : list(str)
            The list of local simulation directories.
            The length of this list is equal to the number of submitted jobs.
        local_input_sample_csv_filename : str
            The name of the local CSV input file.
        local_output_sample_csv_filename : str
            The name of the local CSV output file.
        sample_size : int
            The size of the sample to evaluate.
        block_size : int
            The maximum number of points evaluated within a local simulation.
            The number of jobs required is ceil(sample_size / block_size).
        input_dimension : int
            The input dimension of the model.
        output_dimension : int
            The output dimension of the model.
        input_description : ot.Description(input_dimension)
            The description of the input of the model.
        output_dimension : ot.Description(output_dimension)
            The description of the output of the model.
        """
        if not os.path.isdir(results_directory):
            raise ValueError(f"Directory {results_directory} does not exists")
        self.results_directory = results_directory
        self.simulation_directory_list = simulation_directory_list
        self.local_input_sample_csv_filename = local_input_sample_csv_filename
        self.local_output_sample_csv_filename = local_output_sample_csv_filename
        self.sample_size = sample_size
        self.block_size = block_size
        self.input_dimension = input_dimension
        self.output_dimension = output_dimension
        self.input_description = input_description
        self.output_description = output_description
        number_of_jobs = len(self.simulation_directory_list)
        self.output_file_list = [
            os.path.join(
                self.simulation_directory_list[job_index],
                self.local_output_sample_csv_filename,
            )
            for job_index in range(number_of_jobs)
        ]

    def is_finished(self):
        """
        Returns True if the job is finished.

        Returns
        -------
        is_finished : bool
            True, if all output files are available in the simulation_directory_list.
        """
        number_of_jobs = len(self.simulation_directory_list)
        output_exists_list = [
            os.path.exists(output_file) for output_file in self.output_file_list
        ]
        number_of_existing_output_files = sum(output_exists_list)
        is_finished = number_of_existing_output_files == number_of_jobs
        return is_finished

    def get_input_output(self, verbose=False):
        """
        Returns the inputs and outputs of the job.

        Returns
        -------
        X : ot.Sample(sample_size, input_dimension)
            The input sample.
        Y : ot.Sample(sample_size, output_dimension)
            The output sample.
        """
        X = ot.Sample(self.sample_size, self.input_dimension)
        X.setDescription(self.input_description)
        Y = ot.Sample(self.sample_size, self.output_dimension)
        Y.setDescription(self.output_description)
        number_of_jobs = len(self.simulation_directory_list)
        splitter = ot.KFoldSplitter(self.sample_size, number_of_jobs)
        job_index = 0
        for _, indices in splitter:
            xsimu_dir = self.simulation_directory_list[job_index]
            sub_sample_size = len(indices)
            try:
                # Read input
                input_DOE_file = os.path.join(
                    xsimu_dir, self.local_input_sample_csv_filename
                )
                if verbose:
                    print(f"Read {input_DOE_file}")
                X[indices] = ot.Sample.ImportFromCSVFile(input_DOE_file)
            except FileNotFoundError as err:
                print(err)
                print(
                    f"WARNING: input file {input_DOE_file} could not be read in {xsimu_dir}"
                )
                X[indices] = ot.Sample(
                    [[float("nan")] * self.input_dimension] * sub_sample_size
                )

            try:
                # Read output
                output_DOE_file = os.path.join(
                    xsimu_dir, self.local_output_sample_csv_filename
                )
                if verbose:
                    print(f"Read {output_DOE_file}")
                Y[indices] = ot.Sample.ImportFromCSVFile(output_DOE_file)
            except FileNotFoundError as err:
                print(err)
                print(
                    f"WARNING: output file {output_DOE_file} could not be read in {xsimu_dir}"
                )
                Y[indices] = ot.Sample(
                    [[float("nan")] * self.output_dimension] * sub_sample_size
                )

            job_index += 1
        return X, Y

    def __str__(self):
        """
        Convert the object into a string.

        This method is typically called with the "print" statement.

        Parameters
        ----------
        None.

        Returns
        -------
        s: str
            The string corresponding to the object.
        """
        s = ""
        s += f"results_directory = {self.results_directory}\n"
        s += f"local_input_sample_csv_filename = {self.local_input_sample_csv_filename}\n"
        s += f"local_output_sample_csv_filename = {self.local_output_sample_csv_filename}\n"
        s += f"sample_size = {self.sample_size}\n"
        s += f"block_size = {self.block_size}\n"
        s += f"input_dimension = {self.input_dimension}\n"
        s += f"output_dimension = {self.output_dimension}\n"
        s += f"input_description = {self.input_description}\n"
        s += f"output_description = {self.output_description}\n"
        s += f"Nb. of simulation_directory_list = {len(self.simulation_directory_list)}\n"
        s += f"Nb. of output_file_list = {len(self.output_file_list)}\n"
        return s


class SLURMJobArrayMachine:
    def __init__(
        self,
        model,
        sbatch_wckey,
        user_resources=[],
        base_directory=os.path.abspath(os.path.dirname(__file__)),
        sbatch_extra_options="",
        time_stamp=datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
        sbatch_script_filename="jobarray_launcher.sh",
        study_filename="model.xml",
        physical_model_name="model",
        local_evaluation_script_filename="localSLURMEvaluationFromStudy.py",
        local_input_sample_csv_filename="input_sample.csv",
        local_output_sample_csv_filename="output_sample.csv",
        simulation_directory="simulation_",
        results_directory="work_",
        block_size=1,
        verbose=False,
        python_executable="python3",
    ):
        """
        Create a parallel function evaluated using the jobarray option of SLURM.

        References
        ----------
        - https://slurm.schedmd.com/job_array.html
        - https://slurm.schedmd.com/sbatch.html

        Parameters
        ----------
        model : ot.Function
            The model.
        sbatch_wckey : string
            The WCKEY of the project.
            Please contact your project manager to see which one to use.
            Generates an exception if the key is unknown.
        user_resources : list(string)
            The list of files or directories needed by the model.
            Each file or directory will be copied into the local simulation directory
            where the evaluation is performed.
        base_directory : string
            The directory in which all evaluations are performed.
            The user must have write-access to this directory.
        time_stamp : string
            A time stamp which guarantees that the file names and directories are unique.
        sbatch_script_filename : string
            The filename of the generated sbatch script.
            This file is written in the results_directory.
        sbatch_extra_options : string
            The extra options of sbatch.
            None of these options should contain "array", as this option is
            directly managed by SLURMJobArrayFunction.
            See https://slurm.schedmd.com/sbatch.html for details.
        study_filename : string
            The name of the XML file which contains the physical model.
            This file is generated from the Study class in each local simulation directory.
        physical_model_name : string
            The name of the model in the Study.
        local_evaluation_script_filename : string
            The name of the Python script which evaluates the physical
            model on a single point.
            This script is generated in each simulation_directory.
        local_input_sample_csv_filename : string
            The name of the CSV file containing the input sample in each local simulation directory.
            This file is generated in each simulation_directory by SLURMJobArrayFunction.
        local_output_sample_csv_filename : string
            The name of the CSV file containing the output sample in each local simulation directory.
            This file is generated in each simulation_directory by local_evaluation_script_filename.
        simulation_directory : string
            The prefix of the name of the local simulation directory.
            These directories are sub-directories of results_directory.
        results_directory : string
            The name of the main simulation directory.
        block_size : int
            The maximum number of points evaluated within each local simulation directory.
            The number of jobs required is ceil(sample_size / block_size).
            TODO : check if this parameter can be avoided. Can we evaluate a sample with
            more than 500 points without this option?
        python_executable : str
            The name of the Python binary.
        verbose : bool
            Set to True to print intermediate messages.
        """
        if not isinstance(model, ot.Function):
            raise ValueError(
                f"The model must be a ot.Function, but "
                f"model has type {type(model)}."
            )
        self.model = model
        # Store sbatch options
        checker = WcKeyChecker()
        _, _ = checker.check(sbatch_wckey)
        self.sbatch_wckey = sbatch_wckey
        self.time_stamp = time_stamp
        self.sbatch_script_filename = self.time_stamp + "_" + sbatch_script_filename
        if (
            sbatch_extra_options.find("--array=") != -1
            or sbatch_extra_options.find("-a=") != -1
            or sbatch_extra_options.find("--wckey=") != -1
        ):
            raise ValueError(
                f"The sbatch_extra_options must not contain neither --array or -a or --wckey, "
                f"but sbatch_extra_options = {sbatch_extra_options}."
            )
        self.sbatch_extra_options = sbatch_extra_options
        # Other options
        self.user_resources = user_resources
        self.local_evaluation_script_filename = (
            self.time_stamp + "_" + local_evaluation_script_filename
        )
        self.local_input_sample_csv_filename = (
            self.time_stamp + "_" + local_input_sample_csv_filename
        )
        self.local_output_sample_csv_filename = (
            self.time_stamp + "_" + local_output_sample_csv_filename
        )
        self.study_filename = self.time_stamp + "_" + study_filename
        self.simulation_directory = simulation_directory
        self.physical_model_name = physical_model_name
        if block_size < 1:
            raise ValueError(
                f"The block_size cannot be lower than 1, but block_size = {block_size}"
            )
        self.block_size = block_size
        self.verbose = verbose
        # Create working directory
        if not os.path.isdir(base_directory):
            raise ValueError(f"Directory {base_directory} does not exists")
        self.base_directory = base_directory
        self.results_directory = os.path.join(
            self.base_directory, results_directory + self.time_stamp
        )
        self.python_executable = python_executable
        try:
            if self.verbose:
                print(f"Create {self.results_directory}")
            os.mkdir(self.results_directory)
        except FileExistsError as err:
            print(err)
            print(
                f"WARNING: the following folder already existed: {self.results_directory}"
            )
            pass
        self.job_index = 0

    def create(self, X):
        """
        Creates the job for input sample X.

        This function implements _exec_sample() so that the sample is
        evaluated in N different local simulation directories.
        Each local simulation directory is first created.
        Then the associated user_resources are copied in this local simulation directory.
        All simulations are performed using the "array" option of SLURM.
        SLURMJobArrayFunction waits until all the results are available, then
        gathers the data in all local simulation directories.

        Parameters
        ----------
        X : OpenTURNS.Sample
            The input sample.

        Returns
        -------
        Y : OpenTURNS.Sample
            The output sample.
        """
        X = ot.Sample(X)  # ot.MemoryView > ot.Sample
        sample_size = X.getSize()
        # Compute the number of jobs and split the sample
        number_of_jobs = int(math.ceil(sample_size / self.block_size))
        sample_size = X.getSize()
        splitter = ot.KFoldSplitter(sample_size, number_of_jobs)
        # Build the tree
        simulation_directory_list, job_index_start, job_index_end = self._build_tree(
            X, splitter
        )
        # Write SBATCH script
        sh_file = f"""#!/bin/bash

#SBATCH --wckey={self.sbatch_wckey}
#SBATCH --array={job_index_start}-{job_index_end}

echo "Index $SLURM_ARRAY_TASK_ID"

cd "{self.results_directory}/{self.simulation_directory}$SLURM_ARRAY_TASK_ID"
{self.python_executable} {self.local_evaluation_script_filename}

exit 0
        """
        full_bash_filename = os.path.join(
            self.results_directory, self.sbatch_script_filename
        )
        if self.verbose:
            print(f"Write the jobarray/SLURM bash script {full_bash_filename}")
        with open(full_bash_filename, "w") as file:
            file.write(sh_file)
        # Prepare result
        job = SLURMJobArrayJob(
            self.results_directory,
            simulation_directory_list,
            self.local_input_sample_csv_filename,
            self.local_output_sample_csv_filename,
            sample_size,
            self.block_size,
            self.model.getInputDimension(),
            self.model.getOutputDimension(),
            self.model.getInputDescription(),
            self.model.getOutputDescription(),
        )
        return job

    def submit(self):
        """
        Submit the job.

        Returns
        -------
        command : str
            The sbatch command.
        """
        # Execute
        full_bash_filename = os.path.join(
            self.results_directory, self.sbatch_script_filename
        )
        command = f"sbatch {self.sbatch_extra_options} \"{full_bash_filename}\""
        if self.verbose:
            print(f"Execute {command}")
        otct.execute(command)
        return command

    def copyResources(self, ressources_list, target_directory):
        """
        Copy the resources into the target directory.

        Parameters
        ----------
        ressources_list : list(string)
            The list of files or directories to copy.
        target_directory : string
            The name of the target directory.
        """
        if not os.path.isdir(target_directory):
            raise ValueError(f"Target directory {target_directory} does not exists.")

        ressources_len = len(ressources_list)
        for i in range(ressources_len):
            ressource_item = ressources_list[i]
            if os.path.isfile(ressource_item):
                if self.verbose:
                    print(f"Copy file {ressource_item} to {target_directory}")
                shutil.copy(ressource_item, target_directory)
            elif os.path.isdir(ressource_item):
                basedir = os.path.basename(ressource_item)
                targetpath = os.path.join(target_directory, basedir)
                if self.verbose:
                    print(f"Copy directory {ressource_item} to {targetpath}")
                shutil.copytree(ressource_item, targetpath)
            else:
                raise ValueError(f"Cannot manage ressource {ressource_item}")
        return

    def _build_tree(self, X, splitter):
        """
        Builds the tree of results folders corresponding to X.

        These directories ensure that the different nodes of the cluster
        write the function evaluations into independent files.
        The results of each evaluation of the black-box model
        are stored in the following structure:

        ├── work_26-08-2024_14-57
        |    ├── jobarray_launcher.sh
        |    ├── simulation_0
        |    ├── simulation_1
        |    ├── ...

        Parameters
        ----------
        X : OpenTURNS.Sample
            Input design of experiment to be evaluated.
        splitter : ot.Splitter
            The object which splits the sample into small sub-samples with maximum
            size equal to block_size.
        """
        job_index_start = self.job_index
        simulation_directory_list = []
        for _, indices in splitter:
            xsimu_dir = os.path.join(
                self.results_directory, f"{self.simulation_directory}{self.job_index}"
            )
            simulation_directory_list.append(xsimu_dir)
            if self.verbose:
                print("Create directory = ", xsimu_dir)
            try:
                os.mkdir(xsimu_dir)
            except FileExistsError as err:
                print(err)
                print(f"WARNING: the following folder already existed: {xsimu_dir}")
                pass

            # Create local DOE in the simulation directory
            local_DoE = X[
                indices
            ]  # The sub-sample corresponding to the local simulation
            local_input_sample = ot.Sample(local_DoE)
            input_DOE_file = os.path.join(
                xsimu_dir, self.local_input_sample_csv_filename
            )
            if self.verbose:
                print(f"Job index = {self.job_index}, indices = {indices}")
                print(f"Create local DOE = {input_DOE_file}")
            local_input_sample.setDescription(self.model.getInputDescription())
            local_input_sample.exportToCSVFile(input_DOE_file)
            # Create the local evaluation
            localEvaluationScript = f"""
import openturns as ot
import os
import sys

# Load the model
study = ot.Study()
study.setStorageManager(ot.XMLStorageManager("{self.study_filename}"))
study.load()
model = ot.Function()
study.fillObject("{self.physical_model_name}", model)
outputDimension = model.getOutputDimension()

# If output already exists, do not evaluate the model
if os.path.isfile("{self.local_output_sample_csv_filename}"):
    print("Output file already exists: done.")
    sys.exit(0)

# Read input data
input_sample = ot.Sample.ImportFromCSVFile("{self.local_input_sample_csv_filename}")
print("X = ")
print(input_sample)

# Evaluate the model
try:
    print("Compute Y")
    output_sample = model(input_sample)
except BaseException as err:
    sample_size = input_sample.getSize()
    output_sample = ot.Sample([[float("nan")] * outputDimension] * sample_size)
    print(f"Cannot evaluate model in directory {xsimu_dir}:", err)

# Write output data
print("Y = ")
print(output_sample)
output_sample.exportToCSVFile("{self.local_output_sample_csv_filename}")
"""
            localEvaluationScript_filename = os.path.join(
                xsimu_dir, self.local_evaluation_script_filename
            )
            if self.verbose:
                print(
                    f"Write the Python evaluation script {localEvaluationScript_filename}"
                )
            with open(localEvaluationScript_filename, "w") as file:
                file.write(localEvaluationScript)
            #
            # Create model in the simulation directory
            study_filename_simu = os.path.join(xsimu_dir, self.study_filename)
            study = ot.Study()
            study.setStorageManager(ot.XMLStorageManager(study_filename_simu))
            study.add(f"{self.physical_model_name}", self.model)
            study.save()
            #
            if self.verbose:
                print(f"Copy resources into {xsimu_dir}")
            # This list is given by the user
            ressources_list = []
            for i in range(len(self.user_resources)):
                ressources_list.append(self.user_resources[i])
            # We add this resource since we created it
            self.copyResources(ressources_list, xsimu_dir)
            # Increate job index
            self.job_index += 1

        job_index_end = self.job_index - 1
        return simulation_directory_list, job_index_start, job_index_end

    def __str__(self):
        """
        Convert the object into a string.

        This method is typically called with the "print" statement.

        Parameters
        ----------
        None.

        Returns
        -------
        s: str
            The string corresponding to the object.
        """
        s = ""
        s += f"model = {self.model}\n"
        s += f"sbatch_wckey = {self.sbatch_wckey}\n"
        s += f"time_stamp = {self.time_stamp}\n"
        s += f"sbatch_script_filename = {self.sbatch_script_filename}\n"
        s += f"sbatch_extra_options = {self.sbatch_extra_options}\n"
        s += f"user_resources = {self.user_resources}\n"
        s += f"local_evaluation_script_filename = {self.local_evaluation_script_filename}\n"
        s += f"local_input_sample_csv_filename = {self.local_input_sample_csv_filename}\n"
        s += f"local_output_sample_csv_filename = {self.local_output_sample_csv_filename}\n"
        s += f"study_filename = {self.study_filename}\n"
        s += f"simulation_directory = {self.simulation_directory}\n"
        s += f"physical_model_name = {self.physical_model_name}\n"
        s += f"block_size = {self.block_size}\n"
        s += f"verbose = {self.verbose}\n"
        s += f"base_directory = {self.base_directory}\n"
        s += f"results_directory = {self.results_directory}\n"
        s += f"python_executable = {self.python_executable}\n"
        return s
