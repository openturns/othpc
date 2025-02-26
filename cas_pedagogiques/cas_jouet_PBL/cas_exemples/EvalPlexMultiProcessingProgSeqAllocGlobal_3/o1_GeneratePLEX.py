import openturns as ot 

dist_X1 = ot.Uniform(-1,10)
dist_X2 = ot.Uniform(-1,10)

ot.RandomGenerator.SetSeed(0)

distribution = ot.ComposedDistribution([dist_X1,dist_X2])

PLEX = distribution.getSample(2000)

PLEX.exportToCSVFile('PLEXToEvaluate.csv')
