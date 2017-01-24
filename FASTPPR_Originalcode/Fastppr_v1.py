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
import networkx as nx
from collections import defaultdict

#Global variables
G = nx.DiGraph()

def readInputGraph():
    file_Handler = open("C:/Users/useradmin/Desktop/Matin/PPR_with_node_reduction/Cit-HepTh_Output.txt", 'r')

    for line in file_Handler.readlines():
        data = line.rstrip().split(' ')
        if len(data)==2:
            G.add_edge(int(data[0]), int(data[1]))
        elif len(data)==1:
            G.add_edge(int(data[0]), int(data[0]))
    return 

readInputGraph()
        

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
    print "frontier: ", frontier
    print "len(frontier): ", len(frontier)
    return frontier

        
def pprToFrontier(startId, forwardPPRSignificanceThreshold, frontier, inversePPREstimates):
    walkCount = (c/forwardPPRSignificanceThreshold)
    estimate = 0
    print "walkCount: ", walkCount
    for i in range(int(walkCount)):
        currentNode = startId
        while random.random()>teleport_probability and len(G.successors(currentNode))>0 and currentNode not in frontier:
            random_neighbor = random.randint(1, len(G.successors(currentNode)))-1
            currentNode = (G.successors(currentNode))[random_neighbor]
        if currentNode in frontier:
            estimate +=  1/float(inversePPREstimates[currentNode])
            #print "estimate: ", estimate
    print "Estimate from pprToFrontier: ", estimate/float(walkCount)
    return estimate


print "Total number of nodes in graph is: ", len(G.nodes())
pprSignificanceThreshold = 4/float(len(G.nodes())) #small delta
reverse_threshold = math.sqrt(pprSignificanceThreshold) #Epsilon(r)
teleport_probability = 0.2 #Alpha
reversePPRApproximationFactor = 1/float(6) #Beta
c = 350 #Acurracy Parameter
forwardPPRSignificanceThreshold = pprSignificanceThreshold/float(reverse_threshold)
startId = int(input("Please enter the startId: "))
targetId = int(input("Please enter the targetId: "))


def main():
    start_time = time.clock()
    inversePPREstimates = estimateInversePPR(targetId, reversePPRApproximationFactor*reverse_threshold)    
    frontier = computeFrontier(inversePPREstimates, reverse_threshold)
    #print inversePPREstimates[startId]
    if inversePPREstimates[startId] >= reverse_threshold:
        print "Estimate inversePPREstimates[startId]: ", inversePPREstimates[startId]
    else:
        pprToFrontier(startId, forwardPPRSignificanceThreshold, frontier, inversePPREstimates)
    end_time = time.clock()
    total_time = end_time-start_time
    print "total_time:", total_time

main()