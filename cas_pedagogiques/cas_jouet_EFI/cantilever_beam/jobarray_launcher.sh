#!/bin/bash

#SBATCH --output=logs/output.log
#SBATCH --error=logs/error.log
#SBATCH --wckey=P120F:PYTHON

echo ">>>> Beam.exe wrapper index $SLURM_ARRAY_TASK_ID <<<<"

init_dir=$(pwd)
cd $init_dir/results_$1/SIMU_$SLURM_ARRAY_TASK_ID
$init_dir/template/beam -x beam_input.xml

exit 0