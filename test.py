#TESTING FILE!!!
import random

sum = 0
for x in range(10000):
    sigma = 1
    mu = -0.5 * sigma**2  #Ensures mean of ~1

    x = random.lognormvariate(mu, sigma)
    sum+=x

print(sum/10000)

