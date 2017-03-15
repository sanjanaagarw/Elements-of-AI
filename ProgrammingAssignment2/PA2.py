"""
Artificial Intelligence : Programming Assignment 2
Created on 05/01/2016
@author     : Prateek Bhat and Sanjana Agarwal
@desc       : Class to define the node for a bayes network
@version    : uses Python 2.7
"""

from __future__ import division
"""Import libraries"""
import random
import math
from tabulate import tabulate
from collections import defaultdict
import pandas as pd
from  itertools import *
import numpy as np

"Prior sampling"
def priorSampling(countSamples, bayesnetOrder, network ):
    samples = []
    for _ in xrange(countSamples):
        randNumbers = [random.uniform(0,1) for _ in xrange(len(bayesnetOrder))]
        # print randNumbers
        # print bayesnetOrder
        # raw_input()
        dic = {}

        for num, node in izip(randNumbers,bayesnetOrder):
            if len(network[node]['parents'])==0:
                p = network[node]['p']
                if num > p:
                    dic[node]= 'f'
                else:
                    dic[node] = 't'
            else:
                condition = []
                for parents  in network[node]['parents']:
                    condition.append(dic[parents])
                # print "Before",condition
                condition = ','.join(condition)
                # print "after", condition
                if num > network[node]['cpt'][condition]:
                    dic[node]='f'
                else:
                    dic[node]='t'
        # print dic
        # raw_input()
        samples.append(dic)
    return samples

"Rejection Sampling"
def rejectionSampling(countSamples, bayesnetOrder, network, evidence):
    samples = []
    while len(samples)<countSamples:
        randNumbers = [random.uniform(0,1) for _ in xrange(len(bayesnetOrder))]
        dic = {}
        cond = False
        for num, node in izip(randNumbers, bayesnetOrder):
            if len(network[node]['parents']) == 0:
                p = network[node]['p']
                if num > p:
                    dic[node] = 'f'
                else:
                    dic[node] = 't'
                if node in evidence.keys():
                    if dic[node] == evidence[node]:
                        cond = True
                    else:
                        cond = False
                        break

            else:
                condition = []
                for parents in network[node]['parents']:
                    condition.append(dic[parents])
                condition = ','.join(condition)
                if num > network[node]['cpt'][condition]:
                    dic[node] = 'f'
                else:
                    dic[node] = 't'
                if node in evidence.keys():
                    if dic[node] == evidence[node]:
                        cond = True
                    else:
                        cond =False
                        break
        if cond == True:
            samples.append(dic)
    return samples

"Likelihood sampling"
def likelihoodSampling(countSamples, bayesnetOrder, network, evidence):
    samples = []
    while len(samples)<countSamples:
        likelihood = 1
        randNumbers = [random.uniform(0,1) for _ in xrange(len(bayesnetOrder))]
        dic = {}
        for num, node in izip(randNumbers, bayesnetOrder):
            if node in evidence.keys():
                if len(network[node]['parents']) == 0:
                    p = network[node]['p']
                    if evidence[node] == 'f':
                        p = 1-p
                    likelihood *= p
                    dic[node] = evidence[node]
                else:
                    condition = []
                    for parents in network[node]['parents']:
                        condition.append(dic[parents])
                    condition = ','.join(condition)
                    p = network[node]['cpt'][condition]
                    if evidence[node] == 'f':
                        p = 1-p
                    likelihood *= p
                    dic[node] = evidence[node]
            else:
                if len(network[node]['parents']) == 0:
                    p = network[node]['p']
                    if num > p:
                        dic[node] = 'f'
                    else:
                        dic[node] = 't'
                else:
                    condition = []
                    for parents in network[node]['parents']:
                        condition.append(dic[parents])
                    # print "Before",condition
                    condition = ','.join(condition)
                    # print "after", condition
                    if num > network[node]['cpt'][condition]:
                        dic[node] = 'f'
                    else:
                        dic[node] = 't'
        samples.append([dic,likelihood])
    return samples

"Calculate probability for prior and rejection"
def calculateProb(samples, evidence, query):
    """evidence = {A:t, B:f},
       query = [M,E]"""
    countEvidence = 0
    countPrior = 0
    for sample in samples:
        # print sample
        # raw_input()
        # print evidence.keys()
        # raw_input()
        if len(evidence.keys()) > 0:
            for evid in evidence.keys():
                if sample[evid] == evidence[evid]:
                    cond = True
                else:
                    cond = False
            if cond == True:
                countEvidence +=1
                for q in query:
                    if sample[q] == 't':
                        qcond = True
                    else:
                        qcond = False
                if qcond == True:
                    countPrior += 1

        else:
            for q in query:
                if sample[q] == 't':
                    qcond = True
                else:
                    qcond = False
            if qcond == True:
                countPrior += 1
    # print countEvidence
    if countEvidence == 0:
        prob = countPrior/len(samples)
    else:
        prob = countPrior/countEvidence

    return prob
def enumerate_ask(query, evidence, bayesnetOrder, net):
    # print " f", bayesnetOrder
    distribution = {}
    for i in ["t","f"]:
        for q in query:
            evidence[q] = i
            # print evidence
            distribution[i] = enumerate_all(bayesnetOrder, evidence, net)
            del evidence[q]
            # print distribution
            # raw_input()
    sum =0
    for keys in distribution.keys():
        sum += distribution[keys]

    norm = [distribution[keys]/sum for keys in distribution.keys()]
    return norm

def enumerate_all(bayesnetOrder, evidence, net):
    # print bayesnetOrder
    if len(bayesnetOrder) == 0:
        return 1.0
    # bayesnetOrder.reverse()
    # print bayesnetOrder


    Y = bayesnetOrder.pop()
    # print Y
    # raw_input()
    if Y in evidence.keys():
        value = probability(Y,evidence[Y],evidence,net) * enumerate_all(bayesnetOrder, evidence, net)
        bayesnetOrder.append(Y)
        return value
    else:
        summation = 0
        evidence[Y] = "t"
        summation += probability(Y, 't', evidence, net) *enumerate_all(bayesnetOrder, evidence, net)
        evidence[Y] = "f"
        summation += probability(Y, 'f', evidence, net) *enumerate_all(bayesnetOrder, evidence, net)
        del evidence[Y]

        bayesnetOrder.append(Y)
        return summation

def probability(node, truthValue, evidence, network):

    # print evidence,node,truthValue
    # raw_input()
    if len(network[node]['parents']) == 0:
        p = network[node]['p']
    else:
        condition = []
        for parents in network[node]['parents']:
            condition.append(evidence[parents])
        condition = ','.join(condition)
        p = network[node]['cpt'][condition]
    if truthValue == 't':
        return p
    else:
        return 1-p

def calculateforLikelihood(samples,query):
    sumAll = 0
    sumquery = 0
    for sample in samples:
        sumAll += sample[1]
        for q in query:
            if sample[0][q] == 't':
                sumquery += sample[1]
    return sumquery/sumAll



if __name__ == "__main__":

    net = {'B':{'parents':[],'p':0.001},

           'E':{'parents':[],'p':0.002},

           'A':{'parents':['B','E'],'cpt':{'t,t':0.95, 't,f':0.94, 'f,t':0.29, 'f,f':0.001}},

           'J':{'parents':['A'], 'cpt':{'t':0.9, 'f':0.05}},

           'M':{'parents':['A'],'cpt':{'t':0.7, 'f':0.1}}

           }

    bayesnetOrder = ["B", "E", "A", "J", "M"]
    temp = []
    #print temp
    evidence = {}
    query = []
    #for _ in xrange(10):
     #   evidence = {'M':'t','J':'f'}
    #  query = ['E']
    print "Program begins\n"
    userInput1 = raw_input()
    algo, noOfSamples = userInput1.split()
    noOfSamples = int(noOfSamples)
    userInput2 = raw_input()
    N,M = map(int,userInput2.split())
    evidence = dict(raw_input().split() for _ in range(N))

    #print "Evidences are", evidence
    #print "N ", N,"M", M
    for q in range(M):
        query = raw_input()
    #print "Query is", query
    if algo == "e":
        bayesnetOrder.reverse()
        inferenceByEnumeration = enumerate_ask(query, evidence, bayesnetOrder, net)
        print query,inferenceByEnumeration[0]
    elif algo == "p":
        samples = priorSampling(noOfSamples,bayesnetOrder,net)
        temp.append(calculateProb(samples,evidence,query))
    elif algo == "r":
        samples = rejectionSampling(noOfSamples, bayesnetOrder, net, evidence)
        temp.append(calculateProb(samples,evidence,query))
    else:
        samples = likelihoodSampling(noOfSamples, bayesnetOrder, net, evidence)
        temp.append(calculateforLikelihood(samples, query))
        # print samples
        # raw_input()
        # temp.append(calculateProb(samples,evidence,query))

    if algo == "p" or algo == "r" or algo == "l":
        array = np.array(temp)
        print query,np.sum(array,0)/len(temp)