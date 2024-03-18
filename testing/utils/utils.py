from colorama import Fore, Style
from argparse import ArgumentParser
import os
import re
import json

# Function to clear the terminal
def clear_terminal():
	os.system('cls||clear')

#Parse command line arguments
def parse_arguments():
	try:
		arg_parser = ArgumentParser()
		arg_parser.add_argument("-n", "--nodes", help="Number of nodes in the test", required = True)
		args = arg_parser.parse_args()
		return args.nodes
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
def get_nodes_count():
	try:
		nodes_count = int(parse_arguments())
		if nodes_count != 5 and nodes_count != 10:
			raise ValueError
	except ValueError:
		print(f"{Fore.RED}Invalid number of nodes, exiting...{Fore.RESET}")
		exit(-2)
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Starting the testing process for {nodes_count} clients{Fore.RESET}{Style.NORMAL}\n")
	return nodes_count

# Function that parses the input files from trans0.txt to a list of receiver ids and a list of messages
def parse_input_files(test_input: str):
	receiver_id = []
	message = []
	# Read to the correct trans.txt file according to the node number
	with open('./test_inputs/'+test_input+'.txt', 'r') as file:
		text = file.read()
		lines = text.strip().split('\n')
		for line in lines:
			try:
				match = re.search(r'id(\d+)', line)
				if match:
					# Get the receiver id
					current_receiver_id = (int(match.group(1)))
					receiver_id.append(current_receiver_id)

					# Debugging
					#print(f"Transaction id: {current_receiver_id}")
					# Get message after id and one space after
					current_message = line[match.end():].lstrip()  # Remove the first space from the message
					message.append(current_message)

					# Debugging
					#print(f"Message: {current_message}")
			except re.error as e:
					# Handle exceptions
					print("❌ Parsing Failed ❌")
					print(f"Exception: {e}")
	# All tests passed
	print("✅ Parsing Successful ✅")
	return receiver_id, message
