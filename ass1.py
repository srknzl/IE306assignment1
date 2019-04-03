import simpy
import random

RANDOM_SEED = 978
INTERARRIVAL_RATE = 1/14.3  # exponentially with mean 14.3
SERVICE_RANGE=[10,20]
# UNSKILLED_SERVICE_RANGE = random.lognormvariate(7.2,2.7)

random.seed(RANDOM_SEED)
# Unskilled front end operator, then the expert one. In expert's queue there is beneging

# Unskilled service time lognormally dist with mean 7.2 and std 2.7 mins 

# Reneging follows an independent exponentially distributed time with mean 60 mins.

# Expert takes 3 min breaks after he or she finishes waiting customers. # of break he or she wants to take
# is distributed according to a Poisson dist. with mean 8 breaks per shift.

# Simulate for 1000 cust and 5000 cust seperately



""" 
Collect and report statistics on: 
* Utilization of the front desk operator
* Utilization of the expert operators, 
* Average Total Waiting Time
* Maximum Total Waiting Time to Total System Time Ratio 
* Average number of people waiting to be served by the expert operator


---- Total Waiting Time: Total time a caller waits for both operators
---- Total System Time: The total time a caller spends in the system
"""
service_times = [] #Duration of the conversation between the customer and the operator (Service time)
queue_w_times = [] #Time spent by a customer while it waits for the operator (Queue waiting time Wq)

class Customer(object):
    def __init__(self, name, env):
        self.env = env
        self.name = name
        self.arrival_t = self.env.now
        self.action = env.process(self.call())
    
    def call(self):
        print('%s initiated a call at %g' % (self.name, self.env.now))
 
        with operator.request() as req:
            yield req
            print('%s is assigned to an operator at %g' % (self.name, self.env.now))
            queue_w_times.append(self.env.now - self.arrival_t)
            yield self.env.process(self.ask_question())
            print('%s is done at %g' % (self.name, self.env.now))
        with operator.request() as req:  

           
            
            
    def ask_question(self):
        duration = random.uniform(*SERVICE_RANGE)
        yield self.env.timeout(duration)
        service_times.append(duration)
        
def customer_generator(env):
    """Generate new cars that arrive at the gas station."""
    for i in range(10):
        yield env.timeout(random.expovariate(INTERARRIVAL_RATE))
        customer = Customer('Cust %s' %(i+1), env)  

env = simpy.Environment()
operator = simpy.Resource(env, capacity = 1)
env.process(customer_generator(env, operator,))
env.run()        
print(queue_w_times)
print(queue_w_times)