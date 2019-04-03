import simpy
import random
import numpy as np
"""
Collect and report statistics on: 
* Utilization of the front desk operator = front desk busy /total time
* Utilization of the expert operators
* Average Total Waiting Time
* Maximum Total Waiting Time to Total System Time Ratio 
* Average number of people waiting to be served by the expert operator

---- Total Waiting Time: Total time a caller waits for both operators
---- Total System Time: The total time a caller spends in the system
"""
CUSTOMER_NUMBER = 1000
RANDOM_SEED = 50
random.seed(RANDOM_SEED)

busy_time_expert=0
busy_time_front=0
total_time=0
total_waiting_time=0
total_wait_in_queue2=0

INTERARRIVAL_RATE = 1/14.3
RENEGE_RATE=1/60.0
EXPERT_RATE=1/10.2
BREAK_RATE=1/60.0
last_came=False
service_times = [] #Duration of the conversation between the customer and the front operator (Service time)
service_times2 = [] #Duration of the conversation between the customer and the expert operator (Service time)
queue2_waiting_times=[] # Waiting time of customers in the second queue (expert)

total_waiting_times= []
class Customer(object):
    
    def __init__(self, name, env, opr):
        self.env = env
        self.name = name
        self.arrival_t = self.env.now
        self.action = env.process(self.call())
    
    def call(self):
        print('%s initiated a call at %g' % (self.name, self.env.now))
        total_waiting_time = 0
        with operator.request() as req:
            yield req
            print('%s is assigned to an operator at %g' % (self.name, self.env.now))
            total_waiting_time += self.env.now - self.arrival_t
            yield self.env.process(self.ask_question())
            print('%s is done with 1st operator at %g' % (self.name, self.env.now))
        expert_arrival = self.env.now
        with operator2.request() as req:
            renege_duration = random.expovariate(RENEGE_RATE)
            results = yield req | env.timeout(renege_duration)
            global total_time            
            if req in results:
                print('%s is assigned to an operator2 at %g' % (self.name, self.env.now))
                total_waiting_time += self.env.now - expert_arrival
                queue2_waiting_times.append(self.env.now - expert_arrival)
                total_waiting_times.append(total_waiting_time)
                yield self.env.process(self.ask_question2())
                print('%s is done with 2nd operator at %g' % (self.name, self.env.now))
                total_time = self.env.now
            else:
                print("Customer "+str(self.name)+" reneged")
                total_time = self.env.now                
            
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
    for i in range(CUSTOMER_NUMBER):
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
break_process = env.process(give_break())
env.run()
for i in service_times:
    busy_time_front += i
for i in service_times2:
    busy_time_expert += i
for i in total_waiting_times:
    total_waiting_time += i 
for i in queue2_waiting_times:
    total_wait_in_queue2 += i

print("Utilization of operator 1 is:" + str(busy_time_front/total_time))
print("Utilization of operator 2 is:" + str(busy_time_expert/total_time))
print("Average total waiting time is:" + str(total_waiting_time/CUSTOMER_NUMBER))
print("Maximum total waiting time to total system time ratio " + str(max(total_waiting_times)/total_time))
print("Average number of people waiting to be served by the expert operator " + str(total_wait_in_queue2/total_time))        