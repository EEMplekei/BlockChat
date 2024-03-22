from utils import utils, routines
from colorama import Fore
import requests

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