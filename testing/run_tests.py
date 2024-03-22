from utils import utils, routines
from colorama import Fore
import requests

# Clear terminal
utils.clear_terminal()

# Step 1. Arg Parse how many nodes to be in the chain
nodes_count = utils.get_nodes_count()

# Step 2. Get the addresses of the nodes
nodes = utils.get_nodes_from_config(nodes_count)

# Step 3. Setup the nodes 
routines.setup_nodes(nodes, block_size=10)

# Step 4. Setup Initial Stake on nodes. Initial staking in all nodes in 10 BCC as in the example
routines.set_initial_stake(nodes, stake=10)

#================= HERE IT STARTS THREADING ==========================
routines.start_tests(nodes)
