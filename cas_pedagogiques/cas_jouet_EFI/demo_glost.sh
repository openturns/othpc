#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:01:00 # 1 minute
#SBATCH --output=out.log
#SBATCH --error=err.log
#SBATCH --wckey=P120F:PYTHON

module load glost

echo -n > tasklist
for i in {1..10}
do
    echo "echo $i" >> tasklist
done
mpirun glost_launch tasklist
rm tasklist