import othpc
import openturns as ot

def product_function(X):
    # othpc.fake_load(5) # Fake CPU load for 5 sec.
    return [X[0] * X[1]]
ot_product = ot.PythonFunction(2, 1, product_function, n_cpus=4)
othpc_product = othpc.DistributedFunction(ot_product, ntasks_per_node=4, nodes_per_job=3, timeout_per_job=5)
distribution = ot.JointDistribution([ot.Uniform(0., 1.), ot.Normal(0., 1.)])
x_sample = distribution.getSample(12) # Monte Carlo sample with size N=10
y_sample = othpc_product(x_sample) # Submits 1 job, across 3 nodes each including 4 evaluations 
print(y_sample)
