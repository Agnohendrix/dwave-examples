'''
Solving problems with Constrained Quadratic Hybrid Solver

Problem setup:

Delivery Truck Packing Problem

Resources:
- 1 truck
- 1 package size
- Up to 100 packages

Things to consider:
- Priority shipping status
- Days since order was placed
- Delivery truck's weight capacity
- Delivery truck's size capacity

CQM Development Process:

1. Write objective and constraints in our problem domain
2. Define binary and/or integer variables for our problem
3. Convert objective and constraints into math statements with binary and/or integer variables
4. Build the CQM model from individual objectives and constraints.

1. Objectives and Constraints:

    Objectives:
    1. Maximize the number of packages selected with priority shipping
    2. Minimize the number of days the packages are in transit

    Constraints:
    1. Do not exceed the maximum number of packages that can fit on the truck(100)
    2. Do not exceed the maximum weight capacity of the truck(300 lbs)

2. Define the variables:

    We need to choose which packages to load onto the delivery truck, so we'll use binary variables

    x_i = 1 if package i is selected
        = 0 if package i is not selected
    
3. Objective and Constraints in math statements

    1. Maximize priority shipping:

    min( -sum(p_i*x_i) from i=0 to i=n)

    p_i = priority of package i
    x_i = decision variable for package i

    2. Minimize wait time:

    min( -sum(d_i*x_i) from i=0 to i=n)

    d_i = number of days since package i was ordered
    x_i = decision variable for package i

    3. Constraint 1 - Select maximum number of packages that can fit inside the truck:

    sum(x_i from i=0 to i=n) = P

    x_i = decision variable for package i
    P = maximum number of packages that can fit on the delivery truck

    Direct implementation of Equality Constraints:

    eq_constraint = (quicksum(x[i] for i in range(num_items)) == max_parcels)

    Constraint 2 - The weight of all packages selected cannot exceed maximu weight of delivery truck

    sum(w_i*x_i from i=0 to i=n) <= W

    w_i = weight of package i 
    x_i = decision variable for package i
    W = Maximum weight for delivery package

    Direct implementation:

    ineq_constraint = (quicksum(weights[i]*x[i] for i in range(num_items)) <= max_weight)

4. Build the CQM

    1. Instantiate a ConstrainedQuadraticModel
    2. Add the objectives to the model
    3. Add the constraints to the model

'''

from dimod import ConstrainedQuadraticModel, CQM, Binary, quicksum
from dwave.system import LeapHybridCQMSampler
import random
import numpy as np


#Setup problem
num_packages = 300

priority = random.choices((1,2,3), k=num_packages)

days_since_order = [random.choice([0,1,2,3]) for i in range(num_packages)]

cost = [random.randint(1, 100) for i in range(num_packages)]

max_weight = 3000
max_parcels = 100

obj_weight_priority = 1.0
obj_weight_days = 1

num_items = len(cost)

cqm = ConstrainedQuadraticModel()

bin_variables = [Binary(i) for i in range(num_items)]

#Build an objective to consider priority shipping
objective1 = -obj_weight_priority * quicksum(priority[i] * bin_variables[i] for i in range(num_items))

#Build an objective to consider number of days since the order was placed
objective2 = -obj_weight_days * quicksum(days_since_order[i] * bin_variables[i] for i in range(num_items))

#Add objectives to the CQM
cqm.set_objective(objective1 + objective2)

#Constraints
#Add the maximum capacity constraint
cqm.add_constraint(quicksum(cost[i] * bin_variables[i] for i in range(num_items)) <= max_weight, label='max_capacity')

#Add the maximum parcel constraint
cqm.add_constraint(quicksum(bin_variables[i] for i in range(num_items)) == max_parcels, label='max_parcels')


# Submit to the CQM sampler
cqm_sampler = LeapHybridCQMSampler()
sampleset = cqm_sampler.sample_cqm(cqm, time_limit=10)
print(sampleset.info)

#Process results
feasible_solutions = np.where(sampleset.record.is_feasible == True)

if len(feasible_solutions[0]):
    #Get the first feasible solution
    first = np.where(sampleset.record[feasible_solutions[0][0]][0] == 1)    

    problem_array = np.zeros((3, 4)).astype(int)
    for i in range(num_items):
        problem_array[-1 * (priority[i]-3)][-1 * (days_since_order[i] - 3)] += 1
    
    print("PROBLEM:")
    print('Days since order was placed')
    print('Priority |   3     2     1     0')
    
    for i in range(3):
        print(str(-1*(i-3)),'        ', str(problem_array[i][0]),'   ',str(problem_array[i][1]),'  ', str(problem_array[i][2]),'    ', str(problem_array[i][3]))
    






