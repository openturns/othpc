#!/bin/bash

#SBATCH --output=logs/output.log
#SBATCH --error=logs/error.log
#SBATCH --wckey=P120F:PYTHON

module load glost

echo ">>>> Beam.exe wrapper glost <<<<"
chmod 777 glost/glost_exe.sh
# Make the tasklist
echo -n > glost/tasklist_$1
for i in ${@:2} # All doe indices are parsed in $@
do  
    echo "./glost/glost_exe.sh  $i" >> glost/tasklist_$1
done
mpirun glost_launch glost/tasklist_$1
# rm tasklist_$1
exit 0