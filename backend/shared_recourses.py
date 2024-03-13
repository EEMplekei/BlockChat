from helper_functions.env_variables import *
from components.node import Node

# Initialize environment variables
try:
	TOTAL_NODES = int(try_load_env('TOTAL_NODES'))
	FEE_RATE = float(try_load_env('FEE_RATE'))
	BLOCK_SIZE = int(try_load_env('BLOCK_SIZE'))
except ValueError as e:
	print(f"{Fore.YELLOW}shared_resources{Fore.RESET}: {Fore.RED} cannot get environment variables{e}{Fore.RESET}")
	exit(1)
 
# Initialize the new node and set it's IP and port (happens in the constructor)
# The node will be a bootstrap node if it's ip and port match the bootstrap node's ip and port
node = Node()
node.register_node_to_cluster()