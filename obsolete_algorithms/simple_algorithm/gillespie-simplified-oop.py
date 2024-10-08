import numpy as np
import matplotlib.pyplot as plt

#import config file - we can use config functions as if they were defined here
#the only difference is that we prefix them with c. (so "function(x) becomes c.function(x)")
import simplifiedconfig as c

class SimpleGillespieModel:
    def __init__(self,initialpop,steps):
        self.currstep = 1         #index of which step we're on
        self.steps = steps        #total steps
        self.narr = [0]*steps     #array of population
        self.narr[0] = initialpop #initialize populationa array
        self.tarr = [0]*steps     #time array
    
    def main(self):
        rng = np.random.default_rng() #create an rng object - think of it as buying the dice we'll roll later

        for i in range(1, self.steps):
            dynamic_rates = {}
            relative_probabilities = {}
            prob_sum = 0
            sum_so_far = 0

            #calculate dynamic rates - that is, the rates given current state of model
            for key in c.base_rates:
                dynamic_rates[key] = c.rate_calculation[key](self)
                prob_sum += dynamic_rates[key]
            #print("sum of probabilities: ", prob_sum)

            #find tau for our current state and update our time array
            #NOTE we invert prob_sum to get the right distribution - is this right?
            tau = rng.exponential(scale = 1/prob_sum) 
            #print("resulting tau = ", tau)
            self.tarr[i] = tau + self.tarr[i-1]

            #calculate relative probability of each event happening
            for key in dynamic_rates:
                relative_probabilities[key] = dynamic_rates[key] / prob_sum

            #NOTE is this approach to selecting an event correct?
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
                #this is the case that the R.V. fell in the probability range of this event
                if uniform < sum_so_far + relative_probabilities[key]:
                    c.base_events[key](self) #call the function for this event
                    #print("matched with key", key, "new n is ", self.narr[i])
                    break
                #R.V. didn't fall in probability range for this event - 
                else:
                    sum_so_far += relative_probabilities[key]
            self.currstep += 1
        return (self.tarr, self.narr)

#plot 10 runs of the simulation
for i in range(10):
    tuple = SimpleGillespieModel(1000,1000).main()
    plt.plot(tuple[0],tuple[1])
plt.xlabel("Time (s)")
plt.ylabel("Population")
plt.show()