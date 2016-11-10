# PayMo digital wallet solutions
   written by Tianpei (Luke) Xie

## Data Clean
The given batch data are well-formated, especially the `message` section, which contains extra commas in sentences. Some sentences even take multiple lines which are very hard to read if we load the `batch_payment.csv` file directly into the dataframe. 

In the `./src` directory, I include the `preprocessing()` method in the `read_map.py` file. This method takes the source and filename of the input file and output the `batch_payment_new.csv` in `./paymo_input/` directory. 


## Solution strategy
The key for solving the problem is to find efficient data structures to infer the graph from transaction data.  



### Data structure
Given transaction data, which includes the _id1_ as sender, and 

