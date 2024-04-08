# Importing necessary modules
import threading
import time
import requests
from colorama import Fore
from helper_functions import parse_arg, parse_input, staking, send_messages, utils
import expected_balance

# Define the global variable to store the total transactions
total_transactions = 0

# Define the function that will be executed by each thread
def threading_function(address, trans_folder, receiver_id_list, messages_list):
    global total_transactions
    
    # Step 6. Send messages
    print(f"{Fore.GREEN}[{threading.current_thread().name}] Sending the messages{Fore.RESET}\n")
    send_messages.send_messages(address, receiver_id_list, messages_list)
    print()

# Clear terminal
utils.clear_terminal()

# Starting the testing process for 5 clients
print(f"{Fore.GREEN}Starting the testing process for 5 clients{Fore.RESET}\n")

# Step 1. Arg Parse how many nodes to be in the chain
nodes = 5

# Getting the addresses of the nodes
print(f"{Fore.GREEN}Getting the addresses of the nodes{Fore.RESET}\n")
address = utils.get_nodes_address(nodes)

# Setting up the nodes
print(f"{Fore.GREEN}Setting up the nodes{Fore.RESET}\n")

# Setting up the initial stake on the nodes
print(f"{Fore.GREEN}Setting up the initial stake (100 BCC) on Node 0{Fore.RESET}\n")
staking.initial_stake(address[0], 100)
print()

# Starting the threads
print(f"{Fore.GREEN}Starting the threads{Fore.RESET}\n")

# Parse input files for all threads first
receiver_id_lists = []
messages_lists = []
for i in range(nodes):
    if nodes == 5:
        trans_folder = f'trans5_{i}'
    elif nodes == 10:
        trans_folder = f'trans10_{i}'
    else:
        print(f"{Fore.RED}Invalid number of nodes{Fore.RESET}")
        exit(1)
    receiver_id_list, messages_list = parse_input.parse_input_files(trans_folder)
    receiver_id_lists.append(receiver_id_list)
    messages_lists.append(messages_list)
    total_transactions += len(receiver_id_list)

# Create and start threads after parsing input files
threads = []
start_time = time.time()
for i in range(nodes):
    address_i = address[i]  # Provide the address here
    receiver_id_list = receiver_id_lists[i]
    messages_list = messages_lists[i]
    thread = threading.Thread(target=threading_function, args=(address_i, trans_folder, receiver_id_list, messages_list), name=f"Thread-{i}")
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

end_time = time.time()
print("All threads have finished execution.\n")

# Collect throughput and block time and write to output files
print(f"{Fore.GREEN}Collecting the throughput and block time{Fore.RESET}")
throughput = total_transactions / (end_time - start_time)

# Wait for 3 seconds before retrieving the chain length to ensure all transactions are processed
time.sleep(3)

# Retrieve the Blockchain length
try:
    response = requests.get(address[0]+'/api/get_chain_length')
    if response.status_code != requests.codes.ok:
        response.raise_for_status()
    else:
        response_json = response.json()
        chain_length = response_json.get('chain_length')
except requests.exceptions.RequestException as e:
    print("❌ Retrieving chain length Failed ❌")
    print(f"Exception: {e}")

# Output results
print("Total Transactions: ", total_transactions)
print(f"Successful Transactions: {send_messages.successful_transactions}\n")
print(f"{Fore.GREEN}Throughput: {throughput} transactions per second{Fore.RESET}")
print(f"Chain Length: {chain_length}")
print(f"{Fore.GREEN}Block Time: {(end_time - start_time) / (chain_length - 1)} seconds{Fore.RESET}")

# Write the results to the output file and name the file accordingly
# if nodes == 5:
#     output_file = "output5.txt"
# elif nodes == 10:
#     output_file = "output10.txt"
# else:
#     print(f"{Fore.RED}Invalid number of nodes{Fore.RESET}")
#     exit(1)

# with open(output_file, "w") as file:
#     file.write(f"Total Transactions: {total_transactions}\n")
#     file.write(f"Successful Transactions: {send_messages.successful_transactions}\n")
#     file.write(f"Throughput: {throughput} transactions per second\n")
#     file.write(f"Chain Length: {chain_length}\n")
#     file.write(f"Block Time: {(end_time - start_time) / (chain_length - 1)} seconds\n")

# Check if the temp balance is correct the expected
print(f"{Fore.GREEN}Checking the temp balance{Fore.RESET}")
for i in range(nodes):
    response = requests.get(address[i]+'/api/get_temp_balance')
    if response.status_code != requests.codes.ok:
        response.raise_for_status()
    else:
        response_json = response.json()
        temp_balance = response_json.get('temp_balance')

        if temp_balance != expected_balance.expected_balance(nodes, i):
            print(f"❌ {Fore.RED}Node {i} temp balance is incorrect{Fore.RESET}")
            print(f"❌ Expected: {expected_balance.expected_balance(nodes, i)}")
            print(f"❌ Actual: {temp_balance}\n")
        else:
            print(f"✅ Node {i} temp balance is correct\n")