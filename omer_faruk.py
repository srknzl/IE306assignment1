import simpy
import random
import numpy as np

RANDOM_SEED = 50
random.seed(RANDOM_SEED)

INTERARRIVAL_RATE = 1/14.3
RENEGE_RATE=1/60.0
EXPERT_RATE=1/10.2
BREAK_RATE=1/60.0
last_came=False
service_times = [] #Duration of the conversation between the customer and the operator (Service time)
service_times2 = []
queue_w_times = [] #Time spent by a customer while it waits for the operator (Queue waiting time Wq)
queue_w_times2 = []

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
            print('%s is done with 1st operator at %g' % (self.name, self.env.now))
        expert_arrival = self.env.now
        with operator2.request() as req:
            renege_duration = random.expovariate(RENEGE_RATE)
            results = yield req | env.timeout(renege_duration)
            if req in results:
                print('%s is assigned to an operator2 at %g' % (self.name, self.env.now))
                queue_w_times2.append(self.env.now - expert_arrival)
                yield self.env.process(self.ask_question2())
                print('%s is done with 2nd operator at %g' % (self.name, self.env.now))
            else:
                pass
                #print("Reneged")

           
                
            
    def ask_question(self):
        m1=7.2                             
        v1=2.7
        mu1=np.log((m1**2/((v1+m1**2)**0.5)))
        variance1=np.log((v1**2+m1**2)/m1**2)
        duration = random.lognormvariate(mu1,variance1**0.5)
        yield self.env.timeout(duration)
        service_times.append(duration)
        
    def ask_question2(self):
        duration = random.expovariate(EXPERT_RATE)
        yield self.env.timeout(duration)
        service_times2.append(duration)
    
def customer_generator(env, operator):
    """Generate new cars that arrive at the gas station."""
    for i in range(100):
        duration = random.expovariate(INTERARRIVAL_RATE)
        yield env.timeout(duration)
        customer = Customer('Cust %s' %(i+1), env, operator)  
    global last_came
    last_came = True  





def give_break():
    while(True):
        if(last_came):
            break
        duration = random.expovariate(1/60.0)
        yield env.timeout(duration)
        if operator2.count == 0:
            with operator2.request() as req:
                yield req
                print("Expert takes a break at " + str(env.now))
                yield env.timeout(3)
                print("Experts comes again")

env = simpy.Environment()
operator = simpy.Resource(env, capacity = 1)
operator2= simpy.Resource(env, capacity = 1)
env.process(customer_generator(env, operator))
env.process(give_break())
env.run() 
print (queue_w_times)
print (service_times)
        