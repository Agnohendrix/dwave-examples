# Copyright [yyyy] [name of copyright owner]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Things to do:
 - Please name this file <demo_name>.py
 - Fill in [yyyy] and [name of copyright owner] in the copyright (top line)
 - Add demo code below
 - Format code so that it conforms with PEP 8
"""
from dwave.system import DWaveSampler, EmbeddingComposite #dwave API
from dimod import BinaryQuadraticModel #dwave API

#set up scenario
pumps = [0,1,2,3]
costs = [   [36, 27],
            [56, 65],
            [48, 36],
            [52, 16]]
flow = [2, 7, 3, 8]
demand = 20
time = [0, 1]

x = [[f'P{p}_AM', f'P{p}_PM'] for p in pumps]
bqm = BinaryQuadraticModel('BINARY') #create BinaryQuadraticModel

#Objective
for p in pumps:
    for t in time:
        bqm.add_variable(x[p][t], costs[p][t]) #add variables for each pump at any time

#Constraint 1: Every pump runs at least once per day
for p in pumps:
    c1 = [(x[p][t], 1) for t in time]
    bqm.add_linear_inequality_constraint(
        c1,
        lb = 1, #lower bound = 1
        ub = len(pumps), #upper bound = 4
        lagrange_multiplier=13,
        label = 'c1_pump_'+str(p)
    )

#Constraint 2: At most 3 pumps per time slot
for t in time:
    c2 = [(x[p][t], 1) for p in pumps]
    bqm.add_linear_inequality_constraint(
        c2,
        constant = -3,
        lagrange_multiplier = 1,
        label = 'c2_time '+str(t)
    )

#Constraint 3: Satisfy the daily demand
c3 = [(x[p][t], flow[p]) for t in time for p in pumps]
bqm.add_linear_equality_constraint(
    c3,
    constant = -demand,
    lagrange_multiplier = 28
)


sampler = EmbeddingComposite(DWaveSampler()) #Define sampler
sampleset = sampler.sample(bqm, num_reads=1000) #QPU is probabilistic, run 1000 times

sample = sampleset.first.sample
total_flow = 0
total_cost = 0

print("\n\tAM\tPM")
for p in pumps:
    printout = 'P' + str(p)
    for time in range(2):
        printout += "\t" + str(sample[x[p][time]])
        total_flow += sample[x[p][time]]+flow[p]
        total_cost += sample[x[p][time]]+costs[p][time]
    print(printout)

print("\nTotal flow:\t", total_flow)
print("Total cost:\t", total_cost, "\n")
                            