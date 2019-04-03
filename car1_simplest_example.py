import simpy

def car(env):
     while True:
         print('Start parking at %d' % env.now)
         parking_duration = 5
         yield env.timeout(parking_duration)

         print('Start driving at %d' % env.now)
         trip_duration = 2
         yield env.timeout(trip_duration)

env = simpy.Environment()
env.process(car(env)) # The Process returned by process() 
#can be used for process interactions (we will cover that in the next section, so we will ignore it for now).
env.run(until=15)