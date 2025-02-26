# Execute some tests
# Sur SciMotors
# $ bash test.sh >>test.output.txt 2>&1

# 1. Run the Beam code
./beam -x beam.xml

# 2. Installe OpenTURNS
#python3 -m pip install openturns ipython black

# 3. Tests
echo "demo_beam.py"
python3 demo_beam.py
echo "demo_beam_inside_directory.py"
python3 demo_beam_inside_directory.py
echo "demo_MemoizeWithCSVFile.py"
python3 demo_MemoizeWithCSVFile.py
echo "demo_OpenTURNSPythonFunction.py"
python3 demo_OpenTURNSPythonFunction.py
echo "demo_SLURM_beam.py"
python3 demo_SLURM_beam.py
echo "demo_SLURM_beam_algorithm.py"
python3 demo_SLURM_beam_algorithm.py
echo "demo_SLURM_beam_blocksize.py"
python3 demo_SLURM_beam_blocksize.py
echo "demo_SLURM_beam_cache.py"
python3 demo_SLURM_beam_cache.py
echo "demo_SLURM_beam_evaluate_experiment.py"
python3 demo_SLURM_beam_evaluate_experiment.py
echo "demo_SLURM_beam_submit_and_gather.py"
python3 demo_SLURM_beam_submit_and_gather.py
echo "demo_SLURM_ishigami.py"
python3 demo_SLURM_ishigami.py
echo "demo_SLURM_flood_fail.py"
python3 demo_SLURM_flood_fail.py
echo "demo_dask_beam.py"
python3 demo_dask_beam.py

