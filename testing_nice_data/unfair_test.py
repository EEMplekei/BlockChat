# This file tests the justice of the system, with 5 nodes and a block size of 5.
# The stake is set to 10 BCC except for one node that the stake is 100BCC.
from utils import utils, routines
import time

nodes_count, block_size = 5, 5

# Clear terminal
utils.clear_terminal()

# Step 2. Get the addresses of the nodes
nodes = utils.get_nodes_from_config(nodes_count=5)

# Step 3. Setup the nodes 
routines.setup_nodes(nodes, block_size=5)

# Step 4. Setup Initial Stake on nodes. Initial staking in all nodes in 10 BCC as in the example
stake, unfair_stake = 10, 100
staked_node = routines.set_unfair_stake(nodes, stake, unfair_stake)

# Step 5. Run the tests
throughput, digestive_throughput, digestion_block = routines.start_tests(nodes, stake, block_size)

#Step 6. Check chain length and temp balances
time.sleep(10)
routines.check_chain_length(nodes, block_size)

# Step 7. Check the temp balances of the nodes
routines.check_temp_balance(nodes)