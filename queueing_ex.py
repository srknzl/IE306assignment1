import simpy
import random

RANDOM_SEED = 978
INTERARRIVAL_RATE = 0.1 
SERVICE_RANGE = [50, 90]
random.seed(RANDOM_SEED)

service_times = [] #Duration of the conversation between the customer and the operator (Service time)
queue_w_times = [] #Time spent by a customer while it waits for the operator (Queue waiting time Wq)

class Customer(object):
    def __init__(self, name, env, opr):
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
            
    def ask_question(self):
        duration = random.uniform(*SERVICE_RANGE)
        yield self.env.timeout(duration)
        service_times.append(duration)
        
def customer_generator(env, operator):
    """Generate new cars that arrive at the gas station."""
    for i in range(10):
        yield env.timeout(random.expovariate(INTERARRIVAL_RATE))
        customer = Customer('Cust %s' %(i+1), env, operator)  

env = simpy.Environment()
operator = simpy.Resource(env, capacity = 1)
env.process(customer_generator(env, operator))
env.run()        
print(queue_w_times)
print(queue_w_times)