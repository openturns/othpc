#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00 # 1 minute
#SBATCH --output=out.log
#SBATCH --error=err.log
#SBATCH --wckey=P120F:PYTHON
#SBATCH --array=1-10 
###SBATCH --array=1-10%5 # Makes two batches of size 5
###SBATCH --array=1-10:2 # Iterates by 2: [1, 3, 5, 7, 9]

echo $SLURM_ARRAY_TASK_ID
exit 0
            