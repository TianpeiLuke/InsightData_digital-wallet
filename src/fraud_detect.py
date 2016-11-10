#  -*- coding: utf-8 -*-

from __future__ import with_statement
import os, sys
import pandas as pd
import numpy as np
import itertools


def feature_1(read_src, read_filename, write_src, write_filename, adjacency_mat, adjacency_index, Df):
    '''
       implement feature 1:

        When anyone makes a payment to another user, they'll be notified if they've never made a transaction with that user before.

        "unverified: You've never had a transaction with this user before. Are you sure you would like to proceed with this payment?"

    '''

    with open(os.path.join(read_src, read_filename), 'r') as fin:
        with open(os.path.join(write_src, write_filename), 'a') as fout:
            n = 0
            for line in fin:
                 if n == 0:
                     n = n + 1
                     pass
                 else:
                     print("item "+ str(n) + ": ")
                     if not is_verified(adjacency_mat, adjacency_index, line):
                         print(" unverified: You\'ve never had a transaction with this user before. Are you sure you would like to proceed with this payment?\n")
                         Df = add_Df(Df, line)
                         adjacency_mat, adjacency_index = add_edge(adjacency_mat, adjacency_index, line)
                         fout.write("unverified\n")
                     else:
                         print("trusted.\n")
                         fout.write("trusted\n")
                     n = n + 1
    fin.close()
    fout.close()        


def feature_2(read_src, read_filename, write_src, write_filename, adjacency_mat, adjacency_index, Df):
    '''
       implement feature 2:

          When users make a payment, they'll be notified of when they're not "a friend of a friend".

           "unverified: This user is not a friend or a "friend of a friend". Are you sure you would like to proceed with this payment?"
    '''

    with open(os.path.join(read_src, read_filename), 'r') as fin:
        with open(os.path.join(write_src, write_filename), 'a') as fout:
            n = 0
            for line in fin:
                 if n == 0:
                     n = n + 1
                     pass
                 else:
                     print("item "+ str(n) + ": ")
                     if not is_2ndFriend(adjacency_mat, adjacency_index, line):
                         print(" unverified: This user is not a friend or a \"friend of a friend\". Are you sure you would like to proceed with this payment?\n")
                         Df = add_Df(Df, line)
                         adjacency_mat, adjacency_index = add_edge(adjacency_mat, adjacency_index, line)
                         fout.write("unverified\n")
                     else:
                         print("trusted.\n")
                         fout.write("trusted\n")
                     n = n + 1
    fin.close()
    fout.close()        



#====================================================================================================
def add_Df(Df, line):
    '''
        add to existing dataframe 
    '''
    (N, p) = Df.shape

    temp = line.strip('\n').split(', ')
    token = temp[0:5]
    columns = Df.columns

    return Df.append(pd.DataFrame([token], columns=columns[0:5], index = [N]))

   

def add_edge(adjacency_mat, adjacency_index, line):
    '''
       add to existing adjacency matrix

    '''
    N = len(adjacency_index)-1 #adjacency_index[max(adjacency_index, key=adjacency_index.get)]

    temp = line.strip('\n').split(', ')
    tokens = temp[0:5]
    node1 = int(tokens[1])
    node2 = int(tokens[2])

    #if any(d['key'] == node1 for d in adjacency_mat):
    try:
        loc = adjacency_index[node1] 
    except (KeyError, IndexError):
        N = N + 1
        dict1 = {'key': node1, 'neighbor': [node2] }
        adjacency_mat.append(dict1) 
        adjacency_index.update({node1: N})
    else:
        adjacency_mat[loc]['neighbor'] = list(set(adjacency_mat[loc]['neighbor'] + [node2]))
        
    
    #if any(d['key'] == node2 for d in adjacency_mat):
    try:
        loc2 = adjacency_index[node2]
    except (KeyError, IndexError):
        N = N + 1
        dict2 = {'key': node2, 'neighbor': [node1]}
        adjacency_mat.append(dict2) 
        adjacency_index.update({node2: N})
    else:
        adjacency_mat[loc2]['neighbor'] = list(set(adjacency_mat[loc2]['neighbor'] + [node1]))
        
    return adjacency_mat, adjacency_index
    

def is_verified(adjacency_mat, adjacency_index, line):
    '''
        if a payment is made before with node1 = key and node2 in neighbor
        then return true otherwise return false       

    '''
    result = False
    temp = line.strip('\n').split(', ')
    tokens = temp[0:5]
    node1 = int(tokens[1])
    node2 = int(tokens[2])
    try:
        loc = adjacency_index[node1] 
    except (KeyError, IndexError):
        #when the sender is not seen
        pass 
    else:      
        # see if the receiver is seen
        result = (node2 in adjacency_mat[loc]['neighbor'])
    
    if result == False:
        try:   # try switch the sender and receiver
            loc2 = adjacency_index[node2]
        except(KeyError, IndexError):
            return False
        else:
            result = (node1 in adjacency_mat[loc2]['neighbor']) 
        

    return result


def is_2ndFriend(adjacency_mat, adjacency_index, line):

    result = False
    temp = line.strip('\n').split(', ')
    tokens = temp[0:5]
    node1 = int(tokens[1])
    node2 = int(tokens[2])
    try:
        loc = adjacency_index[node1] 
    except (KeyError, IndexError):
        #when the sender is not seen
        pass 
    else:      
        # see if id1 is friend to id2
        result = (node2 in adjacency_mat[loc]['neighbor'])
        if result == False:
            # if not, see if is friend of friend
            result = any(node2 in adjacency_mat[adjacency_index[x]]['neighbor'] for x in adjacency_mat[loc]['neighbor'])
      
    if result == False:
        try:   # try switch the sender and receiver
            loc2 = adjacency_index[node2]
        except(KeyError, IndexError):
            return False
        else:
            # if id2 is friend to id1
            result = (node1 in adjacency_mat[loc2]['neighbor']) 
            if result == False:
                # if not, see if is friend of friend
                result = any(node1 in adjacency_mat[adjacency_index[y]]['neighbor'] for y in adjacency_mat[loc2]['neighbor']) 

    return result
     


   