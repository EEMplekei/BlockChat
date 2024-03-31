from colorama import Fore, Style
from argparse import ArgumentParser
import threading
import requests
import os
import re
import json
import time

SUCCESSFUL_TRANSACTIONS = 0

# Function to clear the terminal
def clear_terminal():
	os.system('cls||clear')

#Parse command line arguments
def parse_arguments():
	try:
		arg_parser = ArgumentParser()
		arg_parser.add_argument("-n", "--nodes", help="Number of nodes in the test", required = True)
		arg_parser.add_argument("-b", "--blocksize", help="Number of transactions per block in the test", required = True)
		args = arg_parser.parse_args()
		return args.nodes, args.blocksize
	except Exception as e:
		print(f"{Fore.YELLOW}parse_arguments: {Fore.RED}{e}{Fore.RESET}")
		exit(-1)

# Function to get the addresses of the nodes
def get_nodes_from_config(nodes_count: int):
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Getting the addresses of the nodes{Fore.RESET}{Style.NORMAL}\n")
	with open('../nodes_config.json') as f:
		try:
			nodes_config = json.load(f)
		except json.JSONDecodeError as e:
			print(f"{Fore.RED}JSON Decode Error: {e}{Fore.RESET}")
			exit(-3)

	nodes = {}
	for i, item in enumerate(nodes_config.items()):
		if i >= nodes_count:
			break
		nodes[item[0]] = item[1]

	return nodes

#Get for how many nodes to test for
def get_arguments():
	try:
		nodes_count, block_size = int(parse_arguments())
		if nodes_count not in {5, 10}:
			raise ValueError
		if block_size not in {5, 10, 20}:
			raise ValueError
	except ValueError:
		print(f"{Fore.RED}Invalid number of nodes or block_size, exiting...{Fore.RESET}")
		exit(-2)
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Starting the testing process for {nodes_count} clients and {block_size} block size{Fore.RESET}{Style.NORMAL}\n")
	return nodes_count, block_size

# Function that parses the input files from trans0.txt to a list of receiver ids and a list of messages
def parse_input_files(trans_file: str):
	receiver_id = []
	message = []

	# Read to the correct trans.txt file according to the node number
	with open('./test_inputs/'+trans_file+'.txt', 'r') as file:
		text = file.read()
		lines = text.strip().split('\n')
		for line in lines:
			try:
				match = re.search(r'id(\d+)', line)
				if match:
					# Get the receiver id
					current_receiver_id = (int(match.group(1)))
					receiver_id.append(current_receiver_id)

					# Get message after id and one space after
					current_message = line[match.end():].lstrip()  # Remove the first space from the message
					message.append(current_message)

			except re.error as e:
					# Handle exceptions
					print(f"		{Style.BRIGHT}{Fore.RED}❌ Parsing failed for file {trans_file}.txt {Fore.RESET}{Style.NORMAL}")
					print(f"		Exception: {e}")
	
	# All tests passed
	return receiver_id, message

# Run the parsing for all the inputs files
def parse_all_input_files(nodes_count):
	print(f"\n	{Fore.GREEN}Parsing input files{Fore.RESET}\n")
 
	receiver_id_lists = []
	messages_lists = []
	total_transactions = 0

	for i in range(nodes_count):
		if nodes_count == 5:
			trans_folder = f'nodes_5/trans_{i}'
		elif nodes_count == 10:
			trans_folder = f'nodes_10/trans_{i}'
		else:
			print(f"		{Fore.RED}{Style.BRIGHT}Invalid number of nodes{Style.NORMAL}{Fore.RESET}")
			exit(1)
   
		receiver_id_list, messages_list = parse_input_files(trans_folder)
		receiver_id_lists.append(receiver_id_list)
		messages_lists.append(messages_list)
		total_transactions += len(receiver_id_list)

	print(f"		{Fore.GREEN}✅ Parsed all transactions files{Fore.RESET}\n")
	return receiver_id_lists, messages_lists, total_transactions

def start_threads(nodes, receiver_id_lists, messages_lists):
	
	# Define the function that will be executed by each thread
	def _threading_function(node, address, receiver_id_list, messages_list):
		print(f"		[{threading.current_thread().name}] Sending the messages to {node} with address {address}")
		send_messages(node, address, receiver_id_list, messages_list)
	
	print(f"	{Fore.GREEN}{Style.BRIGHT}➜ Starting threads for {len(nodes)} nodes{Style.NORMAL}{Fore.RESET}\n")

	threads = []
	start_time = time.time()
	for i, (node, address) in enumerate(nodes.items()):
	 
		receiver_id_list, messages_list = receiver_id_lists[i], messages_lists[i]
		thread = threading.Thread(target=_threading_function, args=(node, address, receiver_id_list, messages_list), name=f"Thread-{node}")
		thread.start()
		threads.append(thread)

	# Wait for all threads to finish
	for thread in threads:
		thread.join()

	end_time = time.time()
 
	print(f"\n		{Fore.GREEN}All threads have finished execution.{Fore.RESET}\n")
	return end_time - start_time, SUCCESSFUL_TRANSACTIONS
		
def send_messages(node, address: str, receiver_id_list, message_list):
	global SUCCESSFUL_TRANSACTIONS
	for receiver_id, message in zip(receiver_id_list, message_list):

		# Send the message to the receiver
		try:
			response = requests.post(address+'/api/create_transaction', json={
				"receiver_id": int(receiver_id),
				"payload": message,
				"type_of_transaction": "MESSAGE"
			})

			# Check if the status code is not 200 OK
			if response.status_code != requests.codes.ok:
				# If the status code is not OK, raise an exception
				print('here')
				response.raise_for_status()
			else:
				SUCCESSFUL_TRANSACTIONS += 1
		except requests.exceptions.RequestException as e:
			# Handle exceptions
			print(f"	{Fore.RED}❌ Sending message failed for node {node} with address: {address}")
			print(f"Exception: {e}")
			return False

	# All tests passed
	print(f"		{Fore.GREEN}✅ Messages were send successfully for node {node} with address: {address}{Fore.RESET}")
	return True

def get_chain_length(address):
	# Retrieve the Blockchain length
	try:
		response = requests.get(address+'/api/get_chain_length')

		# Check if the status code is not 200 OK
		if response.status_code != requests.codes.ok:
			response.raise_for_status()
		else:
			response_json = response.json()
			chain_length = response_json.get('chain_length')
	except requests.exceptions.RequestException as e:
		print("	❌ Retrieving chain length Failed")
		print(f"Exception: {e}")
	
	return chain_length
   
def expected_balance(nodes_count, i, stake: int):
	if nodes_count == 5:
			trans_folder = f'nodes_5/trans_{i}'
	elif nodes_count == 10:
		trans_folder = f'nodes_10/trans_{i}'
	else:
		print(f"		{Fore.RED}{Style.BRIGHT}Invalid number of nodes{Style.NORMAL}{Fore.RESET}")
		exit(1)

	balance = 1000
	_, messages_list = parse_input_files(trans_folder)
	for message in messages_list:
		balance -= len(message)
	# Due to staking at the beginning (we are talking about temp_balance, not balance)
	balance -= stake
	return balance

def expected_chain_length(number_of_nodes, blocksize, total_transactions):
    # 2*number_of_nodes-1 is the additional number of transactions that will be sent to the network
    # number_of nodes - 1 for initial transactions 
    # number_of_nodes for the staking transactions
    all_transactions = total_transactions+ 2*number_of_nodes-1
    return (all_transactions  // blocksize) + 1

# Write the blocktime and throughtput with keys the pair (number of nodes,blocksize) to the output file as json format to be used by a script to make graph
def write_file(nodes, block_size, throughput, block_time):
    output_file = "output.txt"
    key = f"({nodes},{block_size})"
    # Read existing contents from the file
    try:
        with open(output_file, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # Update the data with new values
    data[key] = {'block_time': block_time, 'throughput': throughput}

    # Write the updated data back to the file
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)
