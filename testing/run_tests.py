from utils import utils, routines
import time

# Clear terminal
utils.clear_terminal()

# Step 1. Arg Parse how many nodes to be in the chain
nodes_count, block_size = utils.get_arguments()

# Step 2. Get the addresses of the nodes
nodes = utils.get_nodes_from_config(nodes_count)

# Step 3. Setup the nodes 
#routines.setup_nodes(nodes, block_size)

stake  = 10

# Step 4. Setup Initial Stake on nodes. Initial staking in all nodes in 10 BCC as in the example
routines.set_initial_stake(nodes, stake)

# Step 5. Run the tests
throughput, digestion_throughput, digestion_block_time = routines.start_tests(nodes, stake, block_size)

#Step 6. Check chain length
time.sleep(10)
routines.check_chain_length(nodes, block_size)

# Step 7. Write the digestion block_time and throughput with keys the pair (number of nodes, blocksize) to the output file as json format to be used by a script to make graph
routines.write_file(len(nodes), block_size, throughput, digestion_block_time)

# Note!
# The block digestion time is effectively the average time required
# for a block to be processed by the network and added to the chain.
# In the same way, the transaction digestion throughput is the average
# number of transactions that can be processed by the network in second
# (that is added to the blockchain  and not just added to the pending list)