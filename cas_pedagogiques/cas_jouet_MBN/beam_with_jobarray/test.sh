# Charge l'environnement
# module load Miniforge3
# conda activate myenv

# Crée le répertoire d'étude
mkdir /scratch/users/C61372/beam

# Crée l'étude paramétrique
# Crée le fichier /scratch/users/C61372/beam/work/input.csv
python3 runParametricBeam.py

# Lance l'étude paramétrique
sbatch /scratch/users/C61372/beam/work/lance_jobs.sh

# Attendre un peu...

# Rassemble les résultats
# Crée le fichier /scratch/users/C61372/beam/work/output.csv
python3 runGatherResultsBeam.py

# Récupère les fichiers
cp /scratch/users/C61372/beam/work/input.csv .
cp /scratch/users/C61372/beam/work/output.csv .

# Nettoie les répertoires de l'étude paramétrique
rm -r test_*

# Nettoie les répertoires de l'étude paramétrique
rm -r /scratch/users/C61372/beam/work

