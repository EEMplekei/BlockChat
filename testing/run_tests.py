from helper_functions import parse_arg, parse_input, staking, send_messages, utils
import json
from colorama import Fore
import threading

# Define a function to execute steps 5 and 6
def threading_function(address, trans_folder):
   # Step 5. Parsing the input files
    print(f"{Fore.GREEN}[{threading.current_thread().name}] Parsing the input files{Fore.RESET}")
    print()
    receiver_id_list, messages_list = parse_input.parse_input_files(trans_folder)
    print(f"[{threading.current_thread().name}] Receiver ID List: {receiver_id_list}")
    print(f"[{threading.current_thread().name}] Messages List: {messages_list}")
    print()

    # Step 6. Send messages
    print(f"{Fore.GREEN}[{threading.current_thread().name}] Sending the messages{Fore.RESET}")
    print()
    send_messages.send_messages(address, receiver_id_list, messages_list)
    print()

utils.clear_terminal()
print(f"{Fore.GREEN}Starting the testing process{Fore.RESET}")
print()

# Step 1. Arg Parse how many nodes to be in the chain
nodes = int(parse_arg.parse_arguments())

# Step 2. Get the addresses of the nodes
print(f"{Fore.GREEN}Getting the addresses of the nodes{Fore.RESET}")
print()
address = utils.get_nodes_address(nodes)
print()

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

# HERE IT STARTS THREADING ==========================
print(f"{Fore.GREEN}Starting the threads{Fore.RESET}")
print()
# Create and start five threads
threads = []
for i in range(2):
    address_i = address[i]  # Provide the address here
    trans_folder = f'trans{i + 10}'  # Assuming you have folders trans1 to trans5
    thread = threading.Thread(target=threading_function, args=(address_i, trans_folder), name=f"Thread-{i}")
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All threads have finished execution.")

# Collect throughput and block time and write to output files
print(f"{Fore.GREEN}Collecting the throughput and block time{Fore.RESET}")
print()
# not implemented...
