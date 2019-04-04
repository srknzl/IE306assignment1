import simpy
import random
import numpy as np

#---------------------Constants-------------------- 
RANDOM_SEED = 50
random.seed(RANDOM_SEED)
INTERARRIVAL_RATE = 1/14.3
RENEGE_RATE=1/60.0
EXPERT_RATE=1/10.2
BREAK_RATE=1/60.0
#---------------------------------------------------

#-------------------Statistic container definitions------------
service_times = [] #Duration of the conversation between the customer and the front operator (Service time)
service_times2 = [] #Duration of the conversation between the customer and the expert operator (Service time)
queue2_waiting_times=[] # Waiting time of customers in the second queue (expert), used to calculate a statistic
total_waiting_times= [] # Total waiting time is a customer's waiting time in 1st queue + waiting time in 2nd queue. 
# -------------------------------------------------------------------------

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
            print('%s is assigned to the front operator at %g' % (self.name, self.env.now))
            total_waiting_time += self.env.now - self.arrival_t
            yield self.env.process(self.ask_question())
            print('%s is done with the front operator at %g' % (self.name, self.env.now))
        expert_arrival = self.env.now
        with operator2.request() as req:
            renege_duration = random.expovariate(RENEGE_RATE)
            results = yield req | env.timeout(renege_duration)
            global total_time            
            if req in results:
                print('%s is assigned to the expert operator at %g' % (self.name, self.env.now))
                total_waiting_time += self.env.now - expert_arrival
                queue2_waiting_times.append(self.env.now - expert_arrival)
                total_waiting_times.append(total_waiting_time)
                yield self.env.process(self.ask_question2())
                print('%s is done with the expert operator at %g' % (self.name, self.env.now))
                total_time = self.env.now
            else:
                print("---------------Customer "+str(self.name)+" reneged after "+ str(self.env.now - expert_arrival) + " of waiting.")
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
        Customer('Cust %s' %(i+1), env, operator)  
    global last_came
    last_came = True  

def give_break():
    while(True):
        if(last_came and (len(operator.queue) + operator.count + len(operator2.queue) + operator2.count == 0)): 
            break
        duration = random.expovariate(1/60.0)
        yield env.timeout(duration)
        if len(operator2.queue) == 0 and operator2.count == 0:
            with operator2.request() as req:
                yield req
                print("---------------Expert operator takes a break at " + str(env.now))
                yield env.timeout(3)
                print("---------------Expert operator comes again")    


""" ------------------Simulation Running Area------------------  """
last_came = False   
CUSTOMER_NUMBER = 1000  
env = simpy.Environment()
operator = simpy.Resource(env, capacity = 1) # front
operator2= simpy.Resource(env, capacity = 1) # expert 
env.process(customer_generator(env, operator)) 
break_process = env.process(give_break()) # Expert's taking break process

# ----------------Initilization of statistic counters--------------- 
busy_time_expert=0
busy_time_front=0
total_time=0
total_waiting_time=0
total_wait_in_queue2=0
#-------------------------------------------------------------------
#---------------------Run simulation and calculate statistics--------------
print("--------------- CUSTOMER NUMBER 1000 ------------------")
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
#------------------------------------------------------------------------

#---------------------Prepare the environment to run the simulation again with 5000 customers ----------------
CUSTOMER_NUMBER=5000
last_came = False   

print("--------------- CUSTOMER NUMBER 5000 ------------------")
env = simpy.Environment()
operator = simpy.Resource(env, capacity = 1)
operator2= simpy.Resource(env, capacity = 1)
env.process(customer_generator(env, operator))
break_process = env.process(give_break())
#------------------Initialization of statistic counters------------------
busy_time_expert = 0
busy_time_front = 0
total_waiting_time = 0
total_waiting_times = []
total_wait_in_queue2 = 0
total_time = 0
service_times = []
service_times2 = []
#------------------------------------------------------------------------

#---------------Run and collect statistics ------------------------------
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


"""-----------------------End of simulation running area----------------------"""