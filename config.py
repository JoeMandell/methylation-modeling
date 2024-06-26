import matplotlib.pyplot as plt
from datetime import datetime
#This is the config file for the main gillespie algorithm simulation
#gillespie.py imports event definitions and rates directly from this file
#any changes made to this file will be reflected in gillespie.py next time it is run, 
#assuming they are in the same folder.

#This file has 4 parts: 
# an Event List defining functions which define what a given event does to the state of the model
# an Event Dictionary mapping keys (names of events) to the functions from Event List
# a Rate List defining functions to calculate the rate of a given event occuring, given the state of the model
# a Rate Dictionary mapping keys (names of events, MUST MATCH those in Event Dictionary) to functions from Rate List
# a Misc Functions section, which contains utility functions used elsewhere


#-------Event List-------

#These functions don't take arguments - instead, they take in the state of the model with the `self` argument
#They can access any part of the model state with self.methylated, self.unmethylated, etc. etc.
def maintenance_event(self): 
      self.methylated[self.currstep] = self.methylated[self.currstep-1]+1
      self.unmethylated[self.currstep] = self.unmethylated[self.currstep-1]

def denovo_event(self):
      self.methylated[self.currstep] = self.methylated[self.currstep-1]
      self.unmethylated[self.currstep] = self.unmethylated[self.currstep-1]-1

def demaintenance_event(self):
      self.methylated[self.currstep] = self.methylated[self.currstep-1]
      self.unmethylated[self.currstep] = self.unmethylated[self.currstep-1]+1

def demethylation_event(self):
      self.methylated[self.currstep] = self.methylated[self.currstep-1]-1
      self.unmethylated[self.currstep] = self.unmethylated[self.currstep-1]

#ask anna - is this birth logic correct - specifically the way the binomial is being drawn
def birth_event(self):
      self.methylated[self.currstep] = 0
      #calculate hemimethylated and draw a random binomial to determine how many become unmethylated
      hemimethylated = self.population - (self.methylated[self.currstep-1] + self.unmethylated[self.currstep-1])
      newly_unmethylated = self.rng.binomial(hemimethylated, 0.5)
      self.unmethylated[self.currstep] = self.unmethylated[self.currstep-1] + newly_unmethylated


#-------Event Dictionary-------

#The "strings" in double quotes are keys to these events. 
#They MUST remain the same in the base_events and rate_calculation dictionaries.
#However, the functions following the keys (denovo_event, for example) can be changed, 
#as long as the function is valid and defined in this file.

base_events = {"maintenance methylation":maintenance_event,
               "de novo methylation":denovo_event,
               "maintenance demethylation":demaintenance_event,
               "demethylation":demethylation_event,
               "birth":birth_event
}

#-------Rate List-------

#These functions also take in `self` as their only argument, 
# and access the model the same way as explained above (in event list)
#would it be optimal to calculate hemimethylated as well?

#-----NON-COLLABORATIVE RATES------
def maintenance_rate(self):
      m = self.population
      hemimethylated = m - (self.methylated[self.currstep-1] + self.unmethylated[self.currstep-1])
      rate = self.params["r_hm"] * hemimethylated
      return rate
def denovo_rate(self):
      rate = self.params["r_hm"] * self.unmethylated[self.currstep-1]
      return rate
def demaintenance_rate(self):
      m = self.population
      hemimethylated = m - (self.methylated[self.currstep-1] + self.unmethylated[self.currstep-1])
      rate = self.params["r_hu"] * hemimethylated
      return rate
def demethylation_rate(self):
      rate = self.params["r_mh"] * self.methylated[self.currstep-1]
      return rate

#------COLLABORATIVE RATES------
def maintenance_rate_collaborative(self):
      hemimethylated = self.population - (self.methylated[self.currstep-1] + self.unmethylated[self.currstep-1])
      methylated = self.methylated[self.currstep-1]
      rate = hemimethylated * (self.params["r_hm"] + self.params["r_hm_h"]*hemimethylated + self.params["r_hm_m"]*methylated)
      # print("calculated maintenance rate: ", rate)
      return rate
def denovo_rate_collaborative(self):
      hemimethylated = self.population - (self.methylated[self.currstep-1] + self.unmethylated[self.currstep-1])
      methylated = self.methylated[self.currstep-1]
      unmethylated = self.unmethylated[self.currstep-1]
      rate = unmethylated * (self.params["r_uh"] + self.params["r_uh_h"]*hemimethylated + self.params["r_uh_m"]*methylated)
      # print("calculated denovo rate: ", rate)
      return rate
def demaintenance_rate_collaborative(self):
      hemimethylated = self.population - (self.methylated[self.currstep-1] + self.unmethylated[self.currstep-1])
      unmethylated = self.unmethylated[self.currstep-1]
      rate = hemimethylated * (self.params["r_hu"] + self.params["r_hu_h"]*hemimethylated + self.params["r_hu_u"]*unmethylated)
      # print("calculated demaintenance rate: ", rate)
      return rate
def demethylation_rate_collaborative(self):
      hemimethylated = self.population - (self.methylated[self.currstep-1] + self.unmethylated[self.currstep-1])
      methylated = self.methylated[self.currstep-1]
      unmethylated = self.unmethylated[self.currstep-1]
      rate = methylated * (self.params["r_mh"] + self.params["r_mh_h"]*hemimethylated + self.params["r_mh_u"]*unmethylated)
      # print("calculated demethylation rate: ", rate)
      return rate

#TODO: expose birth rate as a param
def birth_rate(self):
      return self.params["birth_rate"]
      # b = 1
      # rate = b
      # return rate

#-------Rate Dictionary-------

#Same as with base_rates, the first part ("de novo methylation") 
# should NOT be changed and MUST match an event in base_events
#However, the second part (denovo_rate) can be changed to any desired valid function
rate_calculation = {
                    "maintenance methylation":maintenance_rate_collaborative,
                    "de novo methylation":denovo_rate_collaborative,
                    "birth":birth_rate,
                    "maintenance demethylation":demaintenance_rate_collaborative,
                    "demethylation":demethylation_rate_collaborative
}

#-------Misc Functions-------

#TODO: add a function to determine if a given run of a simulation is sufficiently bistable or not
#TODO: differentiate switching times for methylated to unmethylated and vice versa


#returns the state of the model - ie, whether it is methylated, unmethylated, or in the middle
def find_state(self,step):
      if (self.methylated[step] / self.population) > 0.7:
            return 1
      if (self.unmethylated[step] / self.population) > 0.7:
            return -1
      return 0

def debug_graph(self, step,show=False, save=False):
      print(("switched from ", self.startstate, " at time = ", self.tarr[step], " and step i =", step))
      plt.plot(self.tarr, self.methylated, color='r')
      plt.plot(self.tarr, self.unmethylated, color='b')
      plt.axvline(x = self.tarr[step])
      plt.xlabel("Time (s)")
      plt.ylabel("Population")
      #if the user wants to save the image, we do that here.
      if save:
            name = make_name_for_output()
            plt.savefig("output/" + name + '.png')
      if show:
            plt.show()
            plt.close()

def make_name_for_output():
      name = str(datetime.now())
      name = name.replace(':', '-')
      name = name.replace(' ', '_')
      name = name.replace('.', '-')
      return name

#the "self" keyword ensures that the attribute following it is drawn from...
#... the specific gillespie.py program that called the function
#for example, if an instance of gillespie.py calls for a maintenance_event function, 
#...self.methylated returns the "methylated" array from that specific program