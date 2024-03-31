import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")
from dataclasses import dataclass

class SimpleGillespieModel:
    def __init__(self,initialpop,steps):
        self.currstep = 1         #index of which step we're on
        self.steps = steps        #total steps
        self.narr = [0]*steps     #array of population
        self.narr[0] = initialpop #initialize populationa array
        self.tarr = [0]*steps     #time array

    def birth_event(self):
        self.narr[self.currstep] = self.narr[self.currstep-1] + 1
        print("ran birth, updated self.n to", self.narr[self.currstep])
    def death_event(self):
        self.narr[self.currstep] = self.narr[self.currstep-1] - 1
        print("ran deatj, updated self.n to", self.narr[self.currstep])

    base_rates = {"birth":0.1,
                  "death":0.1
                }
    
    base_events = {"birth":birth_event,
                   "death":death_event
                }
    
    def main(self):
        rng = np.random.default_rng()
        
        for i in range(1, self.steps):
            dynamic_rates = {}
            relative_probabilities = {}
            prob_sum = 0
            sum_so_far = 0
            print(SimpleGillespieModel.base_rates)
            print(SimpleGillespieModel.base_events)

            #calculate the rates for each rate with the current value of n
            for key in SimpleGillespieModel.base_rates:
                dynamic_rates[key] = self.narr[i-1]*SimpleGillespieModel.base_rates[key]
                prob_sum += dynamic_rates[key]

            print("sum of probabilities: ", prob_sum)
            #find tau for our current state and update our time array
            tau = rng.exponential(scale = 1/prob_sum)

            print("resulting tau = ", tau)
            self.tarr[i] = tau + self.tarr[i-1]

            #calculate relative probability of each event happening
            for key in dynamic_rates:
                relative_probabilities[key] = dynamic_rates[key] / prob_sum

            #we use sum_so_far to "slide" the window of events across the interval [0,1] generated by uniform
            #for a coin flip, for example: relative probabilities are 0.5 heads, 0.5 tails.
            #say uniform generates 0.67
            #for the first key, heads:
            #0.67 < 0+0.5 is false, so we go to the else case and set sum_so_far to 0.5
            #for the second key, tails:
            #0.67 < 0.5+0.5 is true, so we take the event corresponding to the tails case
            #PLEASE OBSERVE: python dictionaries are unordered, so this method shouldn't depend on ...
            #the relative order of the events in any of the dictionaries.
            uniform = rng.uniform() #generate a uniform R.V.
            for key in relative_probabilities:
                if uniform < sum_so_far + relative_probabilities[key]:
                    SimpleGillespieModel.base_events[key](self) #call the function for this event
                    print("matched with key", key, "new n is ", self.narr[i])
                    break
                else:
                    sum_so_far += relative_probabilities[key]
            self.currstep += 1
        return (self.tarr, self.narr)

newModel = SimpleGillespieModel(1000,100)
tuple = newModel.main()
plt.plot(tuple[0],tuple[1])
plt.show()