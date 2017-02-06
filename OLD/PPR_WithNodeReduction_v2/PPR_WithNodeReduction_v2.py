# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import math
import time
import random
import operator
import pandas as pd
import networkx as nx
from collections import defaultdict

results = pd.DataFrame(columns=('start_Node', 'target_Node', 'PPREstimate', 'start_Time', 'end_Time', 'Time taken', 'frontier_Size', 'walkCount',  'walks_Hitting_Frontier', 'nodesCrossed_Count'))

#Global variables
G = nx.DiGraph()
Pg = nx.DiGraph()
exp_UtilOfNodes = {}
hub_NodeSet = set()


def readInputGraph():
    file_Handler = open("C:/Users/useradmin/Desktop/Matin/PPR_without_node_reduction/Cit-HepTh_Output.txt", 'r')

    for line in file_Handler.readlines():
        data = line.rstrip().split(' ')
        if len(data)==2:
            G.add_edge(int(data[0]), int(data[1]))
        elif len(data)==1:
            G.add_edge(int(data[0]), int(data[0]))
    return 


#leng = len(G.nodes())
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
        #if each_Node not in [target_node, start_node]:
        #pred = G.predecessors(each_Node)
        #succ = G.successors(each_Node)
        #for each_pred in pred:
            #for each_succ in succ:
                #G.add_edge(each_pred, each_succ)
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


readInputGraph()
H = int(input("Please enter the number of Hub nodes: "))
construct_HubNodeSet(H)
remove_Nodes()
write_toFile()


print "Length of nodes is: ", len(G.nodes())
pprSignificanceThreshold = 4/float(len(G.nodes())) #small delta
print "pprSignificanceThreshold: ", pprSignificanceThreshold
reverse_threshold = math.sqrt(pprSignificanceThreshold) #Epsilon(r)
print "reverse_threshold: ", reverse_threshold
teleport_probability = 0.2 #Alpha
print "teleport_probability: ", teleport_probability
reversePPRApproximationFactor = 1/float(6) #Beta
print "reversePPRApproximationFactor: ", reversePPRApproximationFactor
pprErrorTolerance = reversePPRApproximationFactor*reverse_threshold #Epsilon(inv)
print "pprErrorTolerance: ", pprErrorTolerance
c = 350 #Acurracy Parameter
print "c: ", c
attributes_Dictionary = {}


def write_Output():
    results.to_csv("C:/Users/useradmin/Desktop/Matin/Python-Projects/PPR_WithNodeReduction_v2/Reduced_PPR_Estimates.csv", index = False)
    return 


def debias(inversePPREstimates, reversePPRSignificanceThreshold, pprErrorTolerance):
    for vId in inversePPREstimates.keys():
        if inversePPREstimates[vId] > reversePPRSignificanceThreshold:
            inversePPREstimates[vId] += pprErrorTolerance/float(2)
            for uId in G.predecessors(vId):
                inversePPREstimates[uId] += ((1-teleport_probability)/float(len(G.successors(uId))))*(pprErrorTolerance/float(2))
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
            deltaPriority = (1-teleport_probability)*(vResidual/float(len(G.successors(uId))))
            inversePPREstimates[uId] +=  deltaPriority
            inversePPRResiduals[uId] +=  deltaPriority
            if(inversePPRResiduals[uId] >= largeResidualThreshold and inversePPRResiduals[uId]-deltaPriority < largeResidualThreshold):
                largeResidualNodes.append(uId)
    
    temp = debias(inversePPREstimates, pprErrorTolerance/reversePPRApproximationFactor, pprErrorTolerance)
    return temp

    
def computeFrontier(inversePPREstimates, reversePPRSignificanceThreshold):
    frontier = set()
    for vId in inversePPREstimates.keys():
        if inversePPREstimates[vId] >= reversePPRSignificanceThreshold:
            for uId in G.predecessors(vId):
                frontier.add(uId)
    print "frontier: ", frontier
    print "len(frontier): ", len(frontier)
    attributes_Dictionary['frontier_Size'] = len(frontier)
    return frontier


def pprToFrontier(startId, forwardPPRSignificanceThreshold, frontier, inversePPREstimates):
    walkCount = c/float(forwardPPRSignificanceThreshold)
    print "walkCount: ", walkCount
    attributes_Dictionary['walkCount'] = walkCount
    walksHittingFrontier = 0
    estimate = 0
    nodesCrossed_Count = 0
    for i in range(int(walkCount)):
        currentNode = startId
        while random.random()>teleport_probability and len(G.successors(currentNode))>0 and currentNode not in frontier:
            nodesCrossed_Count = nodesCrossed_Count+1
            random_neighbor = random.randint(1, len(G.successors(currentNode)))-1
            currentNode = (G.successors(currentNode))[random_neighbor]
        if currentNode in frontier:
            walksHittingFrontier = walksHittingFrontier+1
            estimate = estimate + 1/float(walkCount * inversePPREstimates[currentNode])
    attributes_Dictionary['nodesCrossed_Count'] = nodesCrossed_Count
    attributes_Dictionary['walksHittingFrontier'] = walksHittingFrontier
    attributes_Dictionary['estimate'] = estimate
    print "Estimate before returning is: ", estimate
    return estimate


def main():
    print "Length of nodes is: ", len(G.nodes())
    start_time = time.clock()
    attributes_Dictionary['start_time'] = start_time
    inversePPREstimates = estimateInversePPR(targetId, pprErrorTolerance)
    revesePPRSignificanceThreshold = reverse_threshold
    print "revesePPRSignificanceThreshold: ", revesePPRSignificanceThreshold
    frontier = computeFrontier(inversePPREstimates, revesePPRSignificanceThreshold)
    #print frontier
    #print frontier - set(inversePPREstimates.keys())
    #print inversePPREstimates.keys()
    forwardPPRSignificanceThreshold = pprSignificanceThreshold/float(revesePPRSignificanceThreshold)
    print "forwardPPRSignificanceThreshold: ", forwardPPRSignificanceThreshold
    if inversePPREstimates.get(startId, 0) >= reverse_threshold or startId in frontier:
        print "Source is in Frontier set, Estimate is: ", inversePPREstimates[startId]
        attributes_Dictionary['estimate'] = inversePPREstimates[startId]
        attributes_Dictionary['walkCount'] = 0
        attributes_Dictionary['nodesCrossed_Count'] = 0
        attributes_Dictionary['walksHittingFrontier'] = 0
    else:
        pprToFrontier(startId, forwardPPRSignificanceThreshold, frontier, inversePPREstimates)
    end_time = time.clock()
    attributes_Dictionary['end_time'] = end_time
    print "Time consumed: ", end_time-start_time
    attributes_Dictionary['time_Taken'] = end_time-start_time
    return


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
    results.loc[len(results)] = [attributes_Dictionary['startId'], attributes_Dictionary['targetId'], attributes_Dictionary['estimate'], attributes_Dictionary['start_time'], attributes_Dictionary['end_time'], attributes_Dictionary['time_Taken'], attributes_Dictionary['frontier_Size'], attributes_Dictionary['walkCount'], attributes_Dictionary['walksHittingFrontier'], attributes_Dictionary['walksHittingFrontier']]
    inp = int(input("Please enter 1 to continue and 0 to exit and save results: "))
    if inp == 0:    
        write_Output()
        break