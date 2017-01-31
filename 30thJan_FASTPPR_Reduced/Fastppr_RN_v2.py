# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 01:54:41 2017

@author: useradmin
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import time
import math
import random
import operator
import pandas as pd
import networkx as nx
from collections import defaultdict

#Global variables
G = nx.DiGraph()
results = pd.DataFrame(columns=('start_Node', 'target_Node', 'PPREstimate', 'start_Time', 'end_Time', 'Time taken', 'frontier_Size', 'walkCount',  'walks_Hitting_Frontier', 'nodesCrossed_Count', "PPRtoFrontier()"))
attributes_Dictionary = {}


def readInputGraph():
    file_Handler = open("C:/Users/useradmin/Desktop/Matin/Python-Projects/30thJan_FASTPPR_Reduced/input1.txt", 'r')

    for line in file_Handler.readlines():
        data = line.rstrip().split(' ')
        if len(data)==2:
            G.add_edge(int(data[0]), int(data[1]))
        elif len(data)==1:
            G.add_edge(int(data[0]), int(data[0]))
    return 

readInputGraph()


def write_Output():
    results.to_csv("C:/Users/useradmin/Desktop/Matin/Python-Projects/30thJan_FASTPPR_Reduced/Reduced_PPR_Estimates.csv", index = False)
    return 

Pg = nx.DiGraph()
exp_UtilOfNodes = {}
hub_NodeSet = set()


def construct_HubNodeSet(H):
    pageRank_Vector = nx.pagerank(G, alpha=0.85)     
    for node in G.nodes():
        exp_UtilOfNodes[int(node)] = pageRank_Vector[node]*len(G.successors(node)) 
        
    sortedExp_UtilOfNodes = sorted(exp_UtilOfNodes.items(), key=operator.itemgetter(1))
    sortedExp_UtilOfNodes.reverse()
    
    for i in range(H):
        hub_NodeSet.add(sortedExp_UtilOfNodes[i][0])        
    return


def remove_Nodes():
    for each_Node in hub_NodeSet:
        G.remove_node(each_Node)
    return


def write_toFile():
    file_writer = open('modified_Graph.txt', 'w')
    for each_Edge in G.edges():
        source = each_Edge[0]
        to = each_Edge[1]
        file_writer.write(str(source)+" "+str(to)+"\n")
    file_writer.close()
    return


def debias(inversePPREstimates, reversePPRSignificanceThreshold, pprErrorTolerance):
    for vId in inversePPREstimates.keys():
        if inversePPREstimates[vId] > reversePPRSignificanceThreshold:
            inversePPREstimates[vId] += pprErrorTolerance/float(2)
            for uId in G.predecessors(vId):
                inversePPREstimates[uId] += ((1-teleport_probability)*pprErrorTolerance)/float(2*len(G.successors(uId)))
    return inversePPREstimates
    
    
def estimateInversePPR(targetId, pprErrorTolerance):
    largeResidualNodes = list()
    largeResidualNodes.append(targetId)
    inversePPREstimates = dict()
    inversePPRResiduals = dict()
    inversePPREstimates = defaultdict(lambda:0, inversePPREstimates)
    inversePPRResiduals = defaultdict(lambda:0, inversePPRResiduals)
    inversePPREstimates[targetId] = teleport_probability
    inversePPRResiduals[targetId] = teleport_probability
    
    largeResidualThreshold = pprErrorTolerance*teleport_probability
    while(len(largeResidualNodes)!=0):
        vId = largeResidualNodes[0]
        largeResidualNodes.remove(vId)
        vResidual = inversePPRResiduals[vId]
        inversePPRResiduals[vId] = 0
        for uId in G.predecessors(vId):
            deltaPriority = ((1-teleport_probability)*vResidual)/float(len(G.successors(uId)))
            inversePPREstimates[uId] +=  deltaPriority
            inversePPRResiduals[uId] +=  deltaPriority
            if(inversePPRResiduals[uId] >= largeResidualThreshold and inversePPRResiduals[uId]-deltaPriority < largeResidualThreshold):
                largeResidualNodes.append(uId)

    temp = debias(inversePPREstimates, pprErrorTolerance/reversePPRApproximationFactor, pprErrorTolerance)
    return temp

    
def computeFrontier(inversePPREstimates, reversePPRSignificanceThreshold):
    frontier = set()
    #target = set()
    for vId in inversePPREstimates.keys():
        if inversePPREstimates[vId] >= reversePPRSignificanceThreshold:
            #target.add(vId)
            for uId in G.predecessors(vId):
                frontier.add(uId)
    #frontier = frontier-target            
    print "frontier: ", frontier
    print "len(frontier): ", len(frontier)
    attributes_Dictionary['frontier_Size'] = len(frontier)
    return frontier

        
def pprToFrontier(startId, forwardPPRSignificanceThreshold, frontier, inversePPREstimates):
    walkCount = (c /forwardPPRSignificanceThreshold)
    attributes_Dictionary['walkCount'] = walkCount
    attributes_Dictionary['PPRtoFrontier()'] = "Y"
    walksHittingFrontier = 0
    estimate = 0
    nodesCrossed_Count = 0
    print "walkCount: ", walkCount
    for i in range(int(walkCount)):
        currentNode = startId
        while random.random()>teleport_probability and len(G.successors(currentNode))>0 and currentNode not in frontier:
            random_neighbor = random.randint(1, len(G.successors(currentNode)))-1
            currentNode = (G.successors(currentNode))[random_neighbor]
            nodesCrossed_Count += 1
        if currentNode in frontier:
            walksHittingFrontier += 1
            estimate += inversePPREstimates[currentNode]
            #print "estimate: ", estimate
    estimate = estimate/float(walkCount)
    attributes_Dictionary['nodesCrossed_Count'] = nodesCrossed_Count
    attributes_Dictionary['walksHittingFrontier'] = walksHittingFrontier
    attributes_Dictionary['estimate'] = estimate
    print "Estimate from pprToFrontier: ", estimate
    return estimate


def main():
    start_time = time.clock()
    attributes_Dictionary['start_time'] = start_time
    inversePPREstimates = estimateInversePPR(targetId, reversePPRApproximationFactor*reverse_threshold)    
    frontier = computeFrontier(inversePPREstimates, reverse_threshold)
    print inversePPREstimates[startId]
    if inversePPREstimates[startId] >= reverse_threshold or startId in frontier:
        print "Estimate inversePPREstimates[startId]: ", inversePPREstimates[startId]
        attributes_Dictionary['estimate'] = inversePPREstimates[startId]
        attributes_Dictionary['PPRtoFrontier()'] = "N"
    else:
        pprToFrontier(startId, forwardPPRSignificanceThreshold, frontier, inversePPREstimates)
    end_time = time.clock()
    total_time = end_time-start_time
    attributes_Dictionary['end_time'] = end_time
    print "total_time:", total_time
    attributes_Dictionary['time_Taken'] = end_time-start_time

print "Total number of nodes in graph is: ", len(G.nodes())
print "10% of the nodes are: ", 0.1*len(G.nodes())
H = int(input("Please enter the number of Hub nodes: "))
construct_HubNodeSet(H)
remove_Nodes()
write_toFile()
print "Total number of nodes in graph is: ", len(G.nodes())
pprSignificanceThreshold = 4/float(len(G.nodes())) #small delta
reverse_threshold = math.sqrt(pprSignificanceThreshold) #Epsilon(r)
teleport_probability = 0.2 #Alpha
reversePPRApproximationFactor = 1/float(6) #Beta
c = 350 #Acurracy Parameter
forwardPPRSignificanceThreshold = pprSignificanceThreshold/float(reverse_threshold)
startId = 0
targetId = 0
inp = 1

while inp is 1:
    attributes_Dictionary = {}
    startId = int(input("Please enter start_Node: "))
    attributes_Dictionary['startId'] = startId    
    targetId = int(input("Please enter the targetId: "))
    attributes_Dictionary['targetId'] =  targetId    
    main()
    results.loc[len(results)] = [attributes_Dictionary['startId'], attributes_Dictionary['targetId'], attributes_Dictionary['estimate'], attributes_Dictionary['start_time'], attributes_Dictionary['end_time'], attributes_Dictionary['time_Taken'], attributes_Dictionary['frontier_Size'], attributes_Dictionary.get('walkCount', 0), attributes_Dictionary.get('walksHittingFrontier', 0), attributes_Dictionary.get('nodesCrossed_Count', 0), attributes_Dictionary['PPRtoFrontier()']]
    inp = int(input("Please enter 1 to continue and 0 to exit and save results: "))
    if inp == 0:    
        write_Output()
        break