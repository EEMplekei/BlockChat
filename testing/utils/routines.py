from colorama import Fore, Style
from sys import platform
from time import sleep
from utils import utils
import json
import matplotlib.pyplot as plt
import time
import requests
import subprocess

total_transactions = 0

# Run something (e.g. a bash script) on each node to start the API
def setup_nodes(nodes, block_size):	
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Setting up the nodes{Fore.RESET}{Style.NORMAL}\n")
	global proc
		
	#If running in Linux run the first script else the MacOS script, suppress output
	if platform == "linux":
		script_path = ['bash', '../deploy/execute_okeanos_gnome.sh', str(len(nodes)), str(block_size)]
	elif platform == "darwin":
		script_path = ['bash', '../deploy/execute_okeanos_gnome.sh', str(len(nodes)), str(block_size)]
	else :
		print(f"	{Fore.LIGHTRED_EX}Unsupported OS, start nodes one you own{Fore.RESET}")
  
	proc = subprocess.Popen(script_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Test if all the nodes are running to continue with benchmarking
	test_all_nodes_are_up(nodes)

# This function checks if all nodes are up, one by one until all are up, take your time to set them up
# When all are up it returns
def test_all_nodes_are_up(nodes):
	
	#Check if the API is available
	def check_api_availability(address):
		try:
			response = requests.get(address+'/api/')
			response.raise_for_status()
			if not response.status_code == 200:
				return False
		except requests.exceptions.RequestException:
			return False
		return True

	for node, address in nodes.items():
		while not check_api_availability(address):
			continue
		print(f"	{Fore.CYAN}Node {Style.BRIGHT}{node}{Style.NORMAL} is up and running{Fore.RESET}")

	#Now we have to wait for the bootstrap to send the the ring, blockchain and the initial transactions
	sleep(1)
	print(f"\n	{Fore.GREEN}All nodes are up and running{Fore.RESET}\n")

def set_initial_stake(nodes, stake : int):
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Setting the initial stake on the nodes{Fore.RESET}{Style.NORMAL}\n")
	
	for node, address in nodes.items():
		try:
			# api client post call
			response = requests.post(address+'/api/set_stake', json={
				"stake": stake
			})
			print(response.elapsed.total_seconds())
			if(response.status_code != 200):
				raise requests.exceptions.HTTPError
			print(f"	{Fore.LIGHTCYAN_EX}Node {Style.BRIGHT}{node}{Style.NORMAL} has set the initial stake{Fore.RESET}")
		except requests.exceptions.HTTPError:
			print(f"	{Fore.RED}{Style.BRIGHT}Node {node} has failed to set the initial stake{Fore.RED}{Style.NORMAL}")
			exit(-4)
		except requests.exceptions.ConnectionError:
			print(f"	{Fore.RED}Node {Style.BRIGHT}{node}{Style.NORMAL} with address {Style.BRIGHT}{address}{Style.NORMAL} seems to be down{Fore.RED}")
			exit(-5)
	print(f"\n	{Fore.GREEN}Initial Stake Set{Fore.RESET}\n")

def start_tests(nodes, stake: int):
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Starting tests for {len(nodes)} nodes{Style.NORMAL}{Fore.RESET}\n")
	global total_transactions
	#Parse all the input files
	receiver_id_lists, messages_lists, total_transactions = utils.parse_all_input_files(len(nodes))

	# Create and start threads after parsing input files
	run_time, successful_transactions = utils.start_threads(nodes, receiver_id_lists, messages_lists)
	
	# Collect throughput and block time and write to output files
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Collecting the throughput and block time{Fore.RESET}{Style.NORMAL}\n")
	
	# Wait for 3 seconds before retrieving the chain length to ensure all transactions are processed
	time.sleep(3)

	chain_length = utils.get_chain_length(list(nodes.values())[0])
	throughput = total_transactions / run_time
	block_time = run_time / (chain_length - 1)

	# Output results
	print(f"	Total Transactions: {total_transactions}")
	print(f"	Successful Transactions: {successful_transactions}")
	print(f"	{Fore.GREEN}Throughput: {throughput} transactions per second{Fore.RESET}")
	print(f"	Chain Length: {chain_length}")
	print(f"	{Fore.GREEN}Block Time: {block_time} seconds{Fore.RESET}\n")
 
	return throughput, block_time

def check_temp_balances(nodes, stake):
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Checking the temp balance{Fore.RESET}{Style.NORMAL}\n")
	
	for i, (node, address) in enumerate(nodes.items()):
	
		response = requests.get(address+'/api/get_temp_balance')
		if response.status_code != requests.codes.ok:
			response.raise_for_status()
		else:
			response_json = response.json()
			temp_balance = response_json.get('temp_balance')

			exp_balance = utils.expected_balance(len(nodes), i, stake)
			if temp_balance != exp_balance:
				print(f"	❌ {Fore.RED}Node {node} temp balance is incorrect{Fore.RESET}")
				print(f"	❌ Expected: {exp_balance}")
				print(f"	❌ Actual: {temp_balance}\n")
			else:
				print(f"	✅ Node {node} temp balance is correct")

def check_chain_length(nodes, block_size):
	time.sleep(5)
 
	# Check if the number of blocks in blockchain is correct
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Checking the chain lengths{Fore.RESET}{Style.NORMAL}\n")
	for i, (node, address) in enumerate(nodes.items()):
		response = requests.get(address+'/api/get_chain_length')
		if response.status_code != requests.codes.ok:
			response.raise_for_status()
		else:
			response_json = response.json()
			chain_length = response_json.get('chain_length')
   
			expected_chain_length = utils.expected_chain_length(nodes, block_size, total_transactions)			
			if chain_length != expected_chain_length:
				print(f"	❌ {Fore.RED}Node {node} chain length is incorrect{Fore.RESET}")
				print(f"	❌ Expected: {expected_chain_length}")
				print(f"	❌ Actual: {chain_length}\n")
			else:
				print(f"	✅ Node {node} chain length is correct\n")

def draw_graphs():
	# Load data from the file
	with open("../output.txt", "r") as file:
		data = json.load(file)

	# Extract keys and corresponding values
	keys = list(data.keys())
	blocktimes = [data[key]["blocktime"] for key in keys]
	throughputs = [data[key]["throughput"] for key in keys]

	# Extract number of nodes and block size from keys for labeling
	node_labels = [key.split(",")[0][1:] for key in keys]
	blocksize_labels = [key.split(",")[1][:-1] for key in keys]

	# Plotting
	plt.figure(figsize=(10, 6))
	bar_width = 0.35
	index = range(len(keys))

	bars1 = plt.bar(index, blocktimes, bar_width, label='Block Time')
	bars2 = plt.bar([i + bar_width for i in index], throughputs, bar_width, label='Throughput')

	plt.xlabel('Number of Nodes, Block Size')
	plt.ylabel('Value')
	plt.title('Block Time and Throughput for Each Node and Block Size combination')
	plt.xticks([i + bar_width / 2 for i in index], [f"{node_labels[i]}, {blocksize_labels[i]}" for i in range(len(keys))])
	plt.legend()

	# Function to add labels on bars
	def add_labels(bars):
		for bar in bars:
			height = bar.get_height()
			plt.annotate('{}'.format(round(height, 2)),
						xy=(bar.get_x() + bar.get_width() / 2, height),
						xytext=(0, 3),
						textcoords="offset points",
						ha='center', va='bottom')

	add_labels(bars1)
	add_labels(bars2)

	plt.tight_layout()
	plt.show()

