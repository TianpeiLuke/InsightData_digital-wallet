#  -*- coding: utf-8 -*-

from __future__ import with_statement
import os, sys, getopt
import pandas as pd
import numpy as np
import itertools
import copy
from read_map import preprocessing, read_df, edge_hash, edge_hash_2nd
#from antifraud import is_verified, add_Df, add_edge, is_2ndFriend, is_4thFriend

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
    

def add_edge_2nd(adjacency_mat_2nd, adjacency_mat, adjacency_index, line):
    N = len(adjacency_index)-1 #adjacency_index[max(adjacency_index, key=adjacency_index.get)]

    temp = line.strip('\n').split(', ')
    tokens = temp[0:5]
    node1 = int(tokens[1])
    node2 = int(tokens[2])

    #if any(d['key'] == node1 for d in adjacency_mat):
    try:
        loc = adjacency_index[node1] 
    except (KeyError, IndexError):
        neighbor_expand = []
        neighbor_expand = neighbor_expand + [node2]
        # find neighbor of neighbor
        try: 
            loc12 = adjacency_index[node2]  
        except (KeyError, IndexError):
            dict1 = {'key': node1, 'neighbor': [node2] }
            adjacency_mat_2nd.append(dict1) 
        else:    
            neighbor_expand = list(set(neighbor_expand + adjacency_mat[loc12]['neighbor']))
            if node1 in neighbor_expand:
                neighbor_expand.remove(node1)
            dict1 = {'key': node1, 'neighbor': neighbor_expand }
            adjacency_mat_2nd.append(dict1) 

            #update other neighbors
            for other in neighbor_expand:
                adjacency_mat_2nd[adjacency_index[other]]['neighbor'].append(node1)
    else:
        neighbor_expand = []
        neighbor_expand = neighbor_expand + [node2]
        # find neighbor of neighbor
        try:
            loc12 = adjacency_index[node2]      
        except (KeyError, IndexError):
            pass            
        else:
            neighbor_expand = list(set(neighbor_expand + adjacency_mat[loc12]['neighbor']))
        #except IndexError:
        #    print(adjacency_mat[loc12])
        #    raise

            if node1 in neighbor_expand:
                neighbor_expand.remove(node1)
            # update others
            for other in neighbor_expand:
                adjacency_mat_2nd[adjacency_index[other]]['neighbor'].append(node1)    
                adjacency_mat_2nd[adjacency_index[other]]['neighbor']= list(set(adjacency_mat_2nd[adjacency_index[other]]['neighbor']))
         
        adjacency_mat_2nd[loc]['neighbor'] = list(set(adjacency_mat_2nd[loc]['neighbor'] + neighbor_expand))
 
    #if any(d['key'] == node2 for d in adjacency_mat):
    try:
        loc2 = adjacency_index[node2]
    except (KeyError, IndexError):
        neighbor_expand2 = []
        neighbor_expand2 = neighbor_expand2 + [node1]
        # find neighbor of neighbor
        try:
            loc21 = adjacency_index[node1] 
        except (KeyError, IndexError):
            dict2 = {'key': node2, 'neighbor': [node1]}
            adjacency_mat_2nd.append(dict2) 
        else:      
            neighbor_expand2 = list(set(neighbor_expand2 + adjacency_mat[loc21]['neighbor']))
            if node2 in neighbor_expand2:
                neighbor_expand2.remove(node2)
            dict2 = {'key': node2, 'neighbor': neighbor_expand2 }
            adjacency_mat_2nd.append(dict2) 

            #update other neighbors
            for other in neighbor_expand2:
                adjacency_mat_2nd[adjacency_index[other]]['neighbor'].append(node2)
    else:
        neighbor_expand2 = []
        neighbor_expand2 = neighbor_expand2 + [node1]
        # find neighbor of neighbor
        try:
            loc21 = adjacency_index[node1]
        except (KeyError, IndexError):
            pass 
        else:      
            neighbor_expand2 = list(set(neighbor_expand2 + adjacency_mat[loc21]['neighbor']))
            if node2 in neighbor_expand2:
                neighbor_expand2.remove(node2)

				    # update others:
            for other in neighbor_expand2:
                adjacency_mat_2nd[adjacency_index[other]]['neighbor'].append(node2)
                adjacency_mat_2nd[adjacency_index[other]]['neighbor']= list(set(adjacency_mat_2nd[adjacency_index[other]]['neighbor']))
        
        adjacency_mat_2nd[loc2]['neighbor'] = list(set(adjacency_mat_2nd[loc2]['neighbor'] + neighbor_expand2))
        
    return adjacency_mat_2nd




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
    '''
        return True if the edge for given line is within 2nd Friendship relationship
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
     


def is_4thFriend(adjacency_mat_2nd, adjacency_index, line):
    '''
        return True if the edge for given line is within 4th Friendship relationship
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
        # see if id1 is within 2nd order friend to id2
        result = (node2 in adjacency_mat_2nd[loc]['neighbor'])
        if result == False:
            # if not, see if is 4th order friend
            result = any(node2 in adjacency_mat_2nd[adjacency_index[x]]['neighbor'] for x in adjacency_mat_2nd[loc]['neighbor'])
      
    if result == False:
        try:   # try switch the sender and receiver
            loc2 = adjacency_index[node2]
        except(KeyError, IndexError):
            return False
        else:
            # if id2 is within 2nd order friend to id1
            result = (node1 in adjacency_mat_2nd[loc2]['neighbor']) 
            if result == False:
                # if not, see if is 4th order friend
                result = any(node1 in adjacency_mat_2nd[adjacency_index[y]]['neighbor'] for y in adjacency_mat_2nd[loc2]['neighbor']) 

    return result







#================================================================================================
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



def feature_3(read_src, read_filename, write_src, write_filename, adjacency_mat, adjacency_index, adjacency_mat_2nd, Df):
    '''
       implement feature 3:

       More generally, PayMo would like to extend this feature to larger social networks. Implement a feature to warn users only when they're outside the "4th degree friends network". 
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
                     if not is_4thFriend(adjacency_mat_2nd, adjacency_index, line):
                         print(" unverified: This user is not within the 4th Friendship relationship. Are you sure you would like to proceed with this payment?\n")
                         Df = add_Df(Df, line)
                         adjacency_mat_copy = []
                         adjacency_mat_copy = copy.deepcopy(adjacency_mat)
                         adjacency_index_copy = []
                         adjacency_index_copy = copy.deepcopy(adjacency_index)
                         adjacency_mat, adjacency_index = add_edge(adjacency_mat, adjacency_index, line)
                         adjacency_mat_2nd = add_edge_2nd(adjacency_mat_2nd, adjacency_mat_copy, adjacency_index_copy, line)
                         fout.write("unverified\n")
                     else:
                         print("trusted.\n")
                         fout.write("trusted\n")
                     n = n + 1
    fin.close()
    fout.close()        


def main(argv):

    if len(argv) != 5:
        print('antifraud.py <inputfile1> <inputfile2> <outputfile1> <outputfile2> <outputfile3>')
        raise SyntaxError

    inputfile1 = argv[0]
    inputfile2 = argv[1]
    outputfile1 = argv[2]
    outputfile2 = argv[3]
    outputfile3 = argv[4]

#    try:
#        opts, args = getopt.getopt(argv, "hi:o:", ["ifile1=", "ifile2=", "ofile1=", "ofile2=", "ofile3="])
#    except getopt.GetoptError:
#        print('antifraud.py -i <inputfile1> <inputfile2> -o <outputfile1> <outputfile2> <outputfile3>')
#        sys.exit(2)
#
#
#    for opt, arg in opts:
#        print("Here\n" + arg)
#        if opt == '-h':
#            print('antifraud.py <inputfile1> <inputfile2> <outputfile1> <outputfile2> <outputfile3>')
#            sys.exit()
#        elif opt in ("-i", "--ifile1"):
#            inputfile1 = arg
#        elif opt in ("-i", "--ifile2"):
#            inputfile2 = arg
#        elif opt in ("-o", "--ofile1"):
#            outputfile1 = arg
#        elif opt in ("-o", "--ofile2"):
#            outputfile2 = arg
#        elif opt in ("-o", "--ofile3"):
#            outputfile3 = arg
#    print('Input file is \n' + inputfile1 + "\n " + inputfile2)
#    print('Output file is \n'+ outputfile1 + "\n " + outputfile2 + "\n " + outputfile3)
    input1_path = os.path.split(inputfile1)
    input2_path = os.path.split(inputfile2)
    if sys.version_info[0] == 3:
       c = input('Do preprocessing first ? (Y/N)')
    else:
       c = raw_input('Do preprocessing first ? (Y/N)')
       
    if c.upper() == 'Y':
        print("Preprocessing...")
        new_filename = preprocessing(input1_path[0], input1_path[1])
        
        print("Load data into data frame")
        Df = read_df(input1_path[0], new_filename)
    else:
        print("Load data into data frame")
        Df = read_df(input1_path[0], input1_path[1])
    adj_mat, adj_index = edge_hash(Df)

    #duplicate
    Df1 = Df.copy()
    adj_mat1 = []
    adj_index1 = []
    adj_mat1 = copy.deepcopy(adj_mat)
    adj_index1 = copy.deepcopy(adj_index)

    #feature 1
    print("Implement Feature 1")
    output1_path = os.path.split(outputfile1)
    feature_1(input2_path[0], input2_path[1], output1_path[0], output1_path[1], adj_mat1, adj_index1, Df1)
      
    #duplicate
    Df1 = Df.copy()
    adj_mat1 = []
    adj_index1 = []
    adj_mat1 = copy.deepcopy(adj_mat)
    adj_index1 = copy.deepcopy(adj_index)
    #feature 2
    print("Implement Feature 2")
    output2_path = os.path.split(outputfile2)
    feature_2(input2_path[0], input2_path[1], output2_path[0], output2_path[1], adj_mat1, adj_index1, Df1)
     
    #duplicate
    Df1 = Df.copy()
    adj_mat1 = []
    adj_index1 = []
    adj_mat1 = copy.deepcopy(adj_mat)
    adj_index1 = copy.deepcopy(adj_index)


    adj_mat_2nd = edge_hash_2nd(adj_mat1, adj_index1)
    adj_mat_2nd1 = []
    adj_mat_2nd1 = copy.deepcopy(adj_mat_2nd)
    #feature 3
    print("Implement Feature 3")
    output3_path = os.path.split(outputfile3)
    feature_3(input2_path[0], input2_path[1], output3_path[0], output3_path[1], adj_mat1, adj_index1, adj_mat_2nd1, Df1)



if __name__ == "__main__":
    main(sys.argv[1:]) 
 


#====================================================================================================