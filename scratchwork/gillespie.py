import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")
from dataclasses import dataclass

#import config file - we can use config functions as if they were defined here
#the only difference is that we prefix them with c. (so "function(x) becomes c.function(x)")
import switching_time_algorithm.config as c

#TODO: convert to use numpy arrays (faster)
#TODO: ask if its ok that arrays are fixed length - this makes optimizing them substantially easier
#TODO: get some examples of ground-truth behavior to check models against
#TODO: ask if they want runs saved, if so how

class GillespieModel:
    def __init__(self,initialpop,steps,param_dict):
        #TODO: find a better (shorter) name for the index than "currstep" - maybe step? i?
        self.population = initialpop
        self.currstep = 1         #index of which step we're on
        self.steps = steps        #total steps
        self.methylated = [0]*steps    
        self.unmethylated = [0]*steps
        self.methylated[0] = initialpop/2 
        self.unmethylated[0] = initialpop/2
        self.tarr = [0]*steps     #time array
        self.rng = np.random.default_rng() 
        #create an rng object - think of it as buying the dice we'll roll later - 
        #we can seed the rng object if we want reproducible results
        #is this initialization unnesceary? can we just point back to the param dict?
        self.params = param_dict


    
    def main(self):
        for i in range(1, self.steps):
            dynamic_rates = {}
            relative_probabilities = {}
            prob_sum = 0
            sum_so_far = 0

            #calculate dynamic rates - that is, the rates given current state of model
            for key in c.rate_calculation:
                dynamic_rates[key] = c.rate_calculation[key](self)
                prob_sum += dynamic_rates[key]
            #print("sum of probabilities: ", prob_sum)

            #find tau for our current state and update our time array
            #NOTE we invert prob_sum to get the right distribution - is this right?
            tau = self.rng.exponential(scale = 1/prob_sum) 
            #print("resulting tau = ", tau)
            self.tarr[i] = tau + self.tarr[i-1]

            #calculate relative probability of each event happening
            #this is the 'width' of the event in the interval (0,1)
            for key in dynamic_rates:
                relative_probabilities[key] = dynamic_rates[key] / prob_sum


            #Select which event happens by comparing a number from a uniform distribution on (0,1)
            #to the various relative probabilities
            uniform = self.rng.uniform() #generate a uniform R.V.
            for key in relative_probabilities:
                #this is the case that the R.V. fell in the probability range of this event
                if uniform < sum_so_far + relative_probabilities[key]:
                    c.base_events[key](self) #call the function for this event
                    #print("matched with key", key, "new n is ", self.narr[i])
                    break
                #R.V. didn't fall in probability range for this event - 
                else:
                    sum_so_far += relative_probabilities[key]
            self.currstep += 1
        return (self.tarr, self.methylated,self.unmethylated)
    #TODO - store the results of each run into a csv file
    #header data - number of steps, population, seed of random number generator?
    #field data - tarr, methylated, unmethylated?
    #Or, just store the configs in the title, or assosciated text file?

#plot 10 runs of the simulation - debugging

# population = 1000
# stepcount = 10000
# for i in range(10):
#     truple = GillespieModel(population,stepcount,default_parameters).main()
#     x = truple[0]
#     #methylated
#     plt.plot(truple[0],truple[1], color='r')
#     #unmethylated
#     plt.plot(truple[0],truple[2], color='b')
# plt.xlabel("Time (s)")
# plt.ylabel("Population")
# plt.show()

#TODO - write a wrapper function to call and time this function, to measure optimization impact