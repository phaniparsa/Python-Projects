import math
import time
import random
import pandas as pd
import networkx as nx

# Reading raw data and building a Graph
file_Handler = open("C:/Users/useradmin/Desktop/Matin/Python-Projects/PPR_without_node_reduction/Cit-HepTh_Output.txt", 'r')
G = nx.DiGraph()

for line in file_Handler.readlines():
    data = line.rstrip().split(' ')
    if len(data)==2:
        G.add_edge(int(data[0]), int(data[1]))
    elif len(data)==1:
        G.add_edge(int(data[0]), int(data[0]))

# Constants
attributes_Dictionary = {}
teleport_probability = 0.2
threshold = 4/float(len(G.nodes()))
attributes_Dictionary['Threshold'] = threshold
reverse_threshold = math.sqrt(threshold)
attributes_Dictionary["Reverse_Threshold"] = reverse_threshold
c = 350
beta = 1/float(6)

# Initialising global lists
InversePPREstimateVector = {}
Target_Set = set()
Frontier_Set = set()
results = pd.DataFrame(columns=('start_Node', 'target_Node', 'start_Time', 'end_Time', 'Time taken', 'PPREstimate', 'Threshold','Reverse_Threshold', 'Additive_Error', 'Frontier_Size', 'number_of_walks',  'walks_Hitting_Frontier', 'number_of_nodesCrossed'))



def frontier():
    ResidualVector = {}
    global Frontier_Set, Target_Set, InversePPREstimateVector
    additive_error = beta*reverse_threshold
    attributes_Dictionary['Additive_Error'] =  additive_error
    flag = 1
    for node in G.nodes():
        if node == target_node:
            InversePPREstimateVector[node] = teleport_probability
            ResidualVector[node] = teleport_probability
        else:
            InversePPREstimateVector[node] = 0
            ResidualVector[node] = 0
    
    a = time.clock()
    while flag == 1:
        flag = 0
        
        
        for node in G.nodes():
            if ResidualVector[node] > teleport_probability*additive_error:
                flag = 1
                #print "len(G.predecessors(node)): ", G.predecessors(node)
                for neighbor_node in G.predecessors(node):
                    delta = (1 - teleport_probability)*(ResidualVector[node]/float(G.out_degree(neighbor_node)))
                    InversePPREstimateVector[neighbor_node] += delta
                    ResidualVector[neighbor_node] += delta
                    if InversePPREstimateVector[neighbor_node] > reverse_threshold:
                        Target_Set.add(neighbor_node)
                        for temp_nod in G.predecessors(neighbor_node):
                            Frontier_Set.add(temp_nod)
                ResidualVector[node] = 0
    b = time.clock()
    print "Time taken for this loop is: ", b-a
    Frontier_Set = Frontier_Set - Target_Set
    attributes_Dictionary["Frontier_Size"] = len(Frontier_Set)
    
    return


    
def fastPpr(start_node, target_node):
    walks_Hitting_Frontier = 0
    attributes_Dictionary["start_Time"] = time.clock()
    number_of_nodesCrossed = 0
    estimate = 0
    frontier()        
    if start_node in Target_Set:
        estimate = InversePPREstimateVector[start_node]
        attributes_Dictionary["number_of_walks"] = 0
    else:
        num_of_walks = int((c*reverse_threshold)/float(threshold))
        attributes_Dictionary["number_of_walks"] = num_of_walks
        number_of_nodesCrossed = 0
        for i in range(num_of_walks):
            current_node = start_node
            temp = random.random()
            while temp > teleport_probability and G.out_degree(current_node) > 0 and current_node not in Frontier_Set:
                number_of_nodesCrossed =  number_of_nodesCrossed+1
                random_neighbor_index = random.randint(1, len(G.successors(current_node)))
                random_neighbor = (G.successors(current_node))[random_neighbor_index - 1]
                print "random_neighbor: ", random_neighbor
                previous_node = current_node
                current_node = random_neighbor
                if current_node in G.successors(current_node) and len(G.successors(current_node))==1:
                    print "current_node: ", current_node
                    print "G.successors(current_node): ", G.successors(current_node)
                    break
                elif (previous_node in G.successors(current_node) and len(G.successors(current_node))==1) and (current_node in G.successors(previous_node) and len(G.successors(current_node))==1):
                    print "current_node: ", current_node
                    print "previous_node: ", previous_node
                    break
            if current_node in Frontier_Set:
                walks_Hitting_Frontier = walks_Hitting_Frontier+1
                estimate += (1/float(num_of_walks))*(InversePPREstimateVector[current_node])
    attributes_Dictionary["number_of_nodesCrossed"] = number_of_nodesCrossed
    attributes_Dictionary["end_Time"] = time.clock()
    attributes_Dictionary["walks_Hitting_Frontier"] = walks_Hitting_Frontier
    attributes_Dictionary["PPREstimate"] =  estimate
    print("estimate : ", estimate)



def write_Output():
    results.to_csv("C:/Users/useradmin/Desktop/Matin/Python-Projects/PPR_without_node_reduction/PPREstimates_withoutNR.csv", index = False)
    return    
inp = 1


while inp is 1:
    start_node = int(input("Please enter start_Node: "))
    target_node = int(input("Please enter target_Node: "))
    attributes_Dictionary["start_Node"] = start_node
    attributes_Dictionary["target_Node"] = target_node
    Target_Set = set()
    Target_Set.add(target_node)
    fastPpr(start_node, target_node)
    attributes_Dictionary["Time taken"] = attributes_Dictionary["end_Time"] - attributes_Dictionary["start_Time"]
    print attributes_Dictionary
    results.loc[len(results)] = [attributes_Dictionary['start_Node'], attributes_Dictionary['target_Node'], attributes_Dictionary['start_Time'], attributes_Dictionary['end_Time'], attributes_Dictionary['Time taken'], attributes_Dictionary['PPREstimate'], attributes_Dictionary['Threshold'], attributes_Dictionary['Reverse_Threshold'], attributes_Dictionary['Additive_Error'], attributes_Dictionary['Frontier_Size'], attributes_Dictionary['number_of_walks'],  attributes_Dictionary['walks_Hitting_Frontier'], attributes_Dictionary['number_of_nodesCrossed']]
    inp = int(input("Please enter 1 if you wish to continue or 0 to save the results and exit: "))
    if inp==0:
        write_Output()