# coding: utf-8 

from __future__ import with_statement
import os, sys, time
import pandas as pd
import numpy as np
import itertools
import operator
import copy

def update_progress(progress):
    '''
        update_progress() : Displays or updates a console progress bar
        Accepts a float between 0 and 1. Any int will be converted to a float.
        A value under 0 represents a 'halt'.
        A value at 1 or bigger represents 100%
    '''
    barLength = 40 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0:s}] {1:3.1f}% {2:s}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def preprocessing(src, filename):
    '''
       the original file is corrupted by extra commas, just drop additional commas
    '''
    truename = os.path.join(src, filename)
    filename_1, filename_ext = os.path.splitext(filename)
    new_filename = filename_1 + "_new" + filename_ext
    writename = os.path.join(src, new_filename)

    fin = open(truename, 'r')
    fout = open(writename, 'a')
    line = fin.readline()
    fout.write(line)
    line = fin.readline()
    i = 1
    while line: 
       commas = line.count(',')
       commas_temp = line.split(', ')
       try:
            int(commas_temp[1])
       except IndexError:
            print(i)
            print(commas_temp)
            line = fin.readline()
            continue
       except (ValueError, SyntaxError):
            print(i)
            print(commas_temp)
            line = fin.readline()
            continue

       if commas > 4:
            temp = line.split(',')
            temp_2= temp[0:5]
            line_s = ", ".join(temp_2)
            fout.write(line_s.strip("\n") + "\n")
       else:
            #temp = ", ".join(line.split(','))
            #fout.write(temp.strip("\n") + "\n")
            fout.write(line)
       line = fin.readline()
       i = i + 1       

    fin.close()
    fout.close()        
    return new_filename   
  

def read_df(src, filename, **kwargs):
    
    ifnrow = False
    for key in kwargs:
        if key == 'nrows':
            nrows = kwargs[key]
            dfBatch = pd.read_csv(os.path.join(src, filename), nrows=nrows, header=0) 
            ifnrow = True      
      
    if not ifnrow:
        dfBatch = pd.read_csv(os.path.join(src, filename), header=0) 
    
    dfBatch.dropna(inplace=True)
    return dfBatch



def edge_hash(dfBatch):
    '''
       build map from dataframe using hash table
    '''
    [nrows, ncols] = dfBatch.shape
    # setup toolbar
    print('Load data frame and build network ... ')
    i = 0
    toolbar_width = min([40, nrows])
    part_sep = int(nrows/toolbar_width)
    update_progress(i/toolbar_width)
  
    # construct adjacency map 
    adjacency_index = []
    adjacency_mat = [] 
    N = 0
    count = 1
    for index, row in dfBatch.iterrows():
        try:
            int(row[1])
        except ValueError:
            print(row[1])
            raise 
        #print(count)    
        node1 = int(row[1])
        node2 = int(row[2])
        dict1 = {'key': node1, 'neighbor': [node2]}
        dict2 = {'key': node2, 'neighbor': [node1]}
        try:
            loc = adjacency_index[node1]        
        except IndexError:
            adjacency_mat.append(dict1) 
            adjacency_index = {node1: N}
            N = 1        
            #print("node " + str(node1) + ", neighbor "+ str([node2]) )   
        except KeyError:
            adjacency_mat.append(dict1) 
            adjacency_index.update({node1: N})
            N = N + 1
            #print("node " + str(node1) + ", neighbor "+ str([node2]) )   
        else:
            adjacency_mat[loc]['neighbor'] = list(set(adjacency_mat[loc]['neighbor'] + [node2]))
            #print("node " + str(node1) + ", neighbor "+ str(adjacency_mat[loc]['neighbor']) )   
        
        try:
            loc2 = adjacency_index[node2]
        except IndexError:
            adjacency_mat.append(dict2) 
            adjacency_index = {node2: N}
            N = 1  
#            print("node " + str(node2) + ", neighbor "+ str([node1]) )   
        except KeyError:
            adjacency_mat.append(dict2) 
            adjacency_index.update({node2: N})
            N = N + 1
#            print("node " + str(node2) + ", neighbor "+ str([node1]) )   
        else:
            adjacency_mat[loc2]['neighbor'] = list(set(adjacency_mat[loc2]['neighbor'] + [node1]))
#            print("node " + str(node2) + ", neighbor "+ str(adjacency_map[loc2]['neighbor']) )   

        if (count % part_sep == 0) or (count == nrows-1): 
            i = i + 1
            update_progress(i/toolbar_width) 

        count = count + 1
    sorted_adj_index = dict(sorted(adjacency_index.items(), key=operator.itemgetter(1)))
    return adjacency_mat, sorted_adj_index  
   
 
def edge_hash_2nd(adjacency_mat, adjacency_index):
    '''
        construct 2nd order adjacency matrix
        for each dictionary
             {'key': id1, 'neighbor': [id2, id3 ...]}
        the neighbor includes all id1's neighbor and id1's neighbor's neighbor   
    '''

    adjacency_mat_2nd = []
    for d in adjacency_mat:
        neighbors = d['neighbor']
        id1 = d['key']
        neighbor_expand = []
        neighbor_expand = neighbor_expand + neighbors
        for neighbor in neighbors:
            loc = adjacency_index[neighbor]
            temp = adjacency_mat[loc]['neighbor']
            neighbor_expand = neighbor_expand + temp
        
        neighbor_expand = list(set(neighbor_expand))
        if id1 in neighbor_expand:
            neighbor_expand.remove(id1)
        adjacency_mat_2nd.append({'key': id1, 'neighbor': neighbor_expand})

    return adjacency_mat_2nd 