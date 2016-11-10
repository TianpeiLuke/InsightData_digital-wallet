# PayMo digital wallet solutions
   written by Tianpei (Luke) Xie

## Data Clean
The given batch data are well-formated, especially the `message` section, which contains extra commas in sentences. Some sentences even take multiple lines which are very hard to read if we load the `batch_payment.csv` file directly into the dataframe. 

In the `./src` directory, I include the `preprocessing()` method in the `read_map.py` file. This method takes the source and filename of the input file and output the `batch_payment_new.csv` in `./paymo_input/` directory. 


## Solution strategy
The key for solving the problem is to find efficient data structures to infer the graph from transaction data.  



### Data structure
Given the transaction data, which include the `id1` as sender, and `id2` as the receiver, we build the adjacency matrix using list of dictionaries, called `adjacency_mat`. Each dictionary has format 

	`{'key': id1, 'neighbor': list of neighbors }`

where the list of neighbors contains all neighbors of `id1` in a transaction network. Similarly for `id2`. Note that each transcation yields two elements in `adjancency_mat`, since the graph is undirected. 

Also, we use a hash table to store the location of each node id in `adjacency_mat`, called `adjacency_index`. `adjacency_index` is a dictionary with keys being the node id, and values being the index of corresponding dictionary element in `adjacency_mat`.

	`adjacency_index = {id1: loc1, id2: loc2, id3: loc3, ... }`
