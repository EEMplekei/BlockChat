import atexit
import signal
from utils import utils, routines
from colorama import Fore
import threading
import time
import requests

#Register the exit handlers
routines.register_exit_handlers()


# Define the global variable to store the total transactions
total_transactions = 0

# Define the function that will be executed by each thread
def threading_function(address, trans_folder):
    global total_transactions
   # Step 5. Parsing the input files
    print(f"{Fore.GREEN}[{threading.current_thread().name}] Parsing the input files{Fore.RESET}")
    print()
    receiver_id_list, messages_list = utils.parse_input_files(trans_folder)
    total_transactions += len(receiver_id_list)
    #print(f"[{threading.current_thread().name}] Receiver ID List: {receiver_id_list}")
    #print(f"[{threading.current_thread().name}] Messages List: {messages_list}")
    #print()

    # Step 6. Send messages
    print(f"{Fore.GREEN}[{threading.current_thread().name}] Sending the messages{Fore.RESET}")
    print()
    utils.send_messages(address, receiver_id_list, messages_list)
    print()

utils.clear_terminal()

# Step 1. Arg Parse how many nodes to be in the chain
nodes_count = utils.get_nodes_count()

# Step 2. Get the addresses of the nodes
nodes = utils.get_nodes_from_config(nodes_count)

# Step 3. Setup the nodes 
routines.setup_nodes(nodes)

# Step 4. Setup Initial Stake on nodes. Initial staking in all nodes in 10 BCC as in the example
routines.set_initial_stake(nodes, 10)
exit()
#================= HERE IT STARTS THREADING ==========================
print(f"{Fore.GREEN}Starting the threads{Fore.RESET}\n")
# Create and start five threads
threads = []
start_time = time.time()
for i in range(nodes):
    address_i = addresses[i]  # Provide the address here
    if nodes == 5:
        trans_folder = f'trans5_{i}'
    elif nodes == 10:
        trans_folder = f'trans10_{i}'
    else:
        print(f"{Fore.RED}Invalid number of nodes{Fore.RESET}")
        exit(1)
    thread = threading.Thread(target=threading_function, args=(address_i, trans_folder), name=f"Thread-{i}")
    thread.start()
    threads.append(thread)

#Wait for all threads to finish
for thread in threads:
    thread.join()

end_time = time.time()
print("All threads have finished execution.")
print()

# Collect throughput and block time and write to output files
print(f"{Fore.GREEN}Collecting the throughput and block time{Fore.RESET}")
throughput = total_transactions / (end_time - start_time)

# Wait for 3 seconds before retrieving the chain length to ensure all transactions are processed
time.sleep(3)
# Retrieve the Blockchain length
try:
    response = requests.get(addresses[0]+'/api/get_chain_length')

    # Check if the status code is not 200 OK
    if response.status_code != requests.codes.ok:
        # If the status code is not OK, raise an exception
        response.raise_for_status()
    else:
        # Extract chain_length from the JSON response
        response_json = response.json()
        chain_length = response_json.get('chain_length')
except requests.exceptions.RequestException as e:
    # Handle exceptions
    print("❌ Retrieving chain length Failed ❌")
    print(f"Exception: {e}")

print("Total Transactions: ", total_transactions)
print(f"{Fore.GREEN}Throughput: {throughput} transactions per second{Fore.RESET}")

print(f"Chain Length: {chain_length}")
# Output the block time excluding the genesis block
print(f"{Fore.GREEN}Block Time: {(end_time - start_time) / (chain_length - 1)} seconds{Fore.RESET}")