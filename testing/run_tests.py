from helper_functions import parse_arg, parse_input, staking, send_messages, utils
import json
from colorama import Fore

utils.clear_terminal()
print(f"{Fore.GREEN}Starting the testing process{Fore.RESET}")
print()

# Step 1. Arg Parse how many nodes to be in the chain
nodes = int(parse_arg.parse_arguments())

# Step 2. Get the addresses of the nodes
print(f"{Fore.GREEN}Getting the addresses of the nodes{Fore.RESET}")
print()
address = utils.get_nodes_address(nodes)

# Step 3. Setup the nodes 
print(f"{Fore.GREEN}Setting up the nodes{Fore.RESET}")
print()


# Step 4. Setup Initial Stake on nodes 
# Initial staking in all nodes in 10 BCC as in the example
print(f"{Fore.GREEN}Setting up the initial stake on the nodes{Fore.RESET}")
print()
for i in range(nodes):
	staking.initial_stake(address[i], 10)
print()


print(f"{Fore.GREEN}Starting the threads{Fore.RESET}")
print()


# HERE IT STARTS THREADING ==========================
# not implemented...


# Step 5. Parsing the input files
print(f"{Fore.GREEN}Parsing the input files{Fore.RESET}")
print()
receiver_id_list, messages_list = parse_input.parse_input_files('trans0')
# print(f"Receiver id list: {receiver_id_list}")
# print(f"Messages list: {messages_list}")
print()

# Step 6. Send messages
print(f"{Fore.GREEN}Sending the messages{Fore.RESET}")
print()
send_messages.send_messages(address[0], receiver_id_list, messages_list)

# Collect throughput and block time and write to output files