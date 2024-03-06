import argparse
import os
import re
import requests
import json

#==============================================================================================
#==============================================================================================
#==============================================================================================
# THIS IS A TEST SCRIPT FOR TESTING THE BLOCKCHAIN NETWORK WITH THE GIVEN TRANSACTION

# HOW TO RUN THIS SCRIPT:
# 1. Open the terminal
# 2. Navigate to the testing directory
# 3. Run the following command to test the first node (node0) with transactions from trans0.txt: 
# 	python test.py -t 0
# 4. And so on for the rest of the nodes

# IMPORTANT:
# The addresses of the nodes are stored in the nodes_config.json file
#==============================================================================================
#==============================================================================================
#==============================================================================================

# Opening JSON file
f = open('nodes_config.json')
nodes_config = json.load(f)
f.close()

# ARGUMENTS
argParser = argparse.ArgumentParser()
argParser.add_argument("-t", "--test", help="Port in which node is running", type=int)
args = argParser.parse_args()
# Address of node
t = args.test

# Networking Configuration
address = nodes_config.get(f'node{t}') if t in range(10) else print("Invalid node number") and exit()

# Read to the correct trans.txt file according to the node number
with open('trans'+str(t)+'.txt', 'r') as file:
	text = file.read()
	lines = text.strip().split('\n')
	for line in lines:
		match = re.search(r'id(\d+)', line)
		if match:
			# Get the transaction id
			receiver_id = (int(match.group(1)))
			print(f"Transaction id: {receiver_id}")
			# Get message after id and one space after
			message = line[match.end():].lstrip()  # Remove the first space from the message
			print(f"Message: {message}")

			# TESTED UNTIL HERE   <--->   WORKS FINE
			# Could not test the rest of the code because the API is not available (epaize allos me tis masines)

			# Send the transaction to the node
			try:
				# api client call  for message
				response = requests.post(address+'/api/create_transaction', json={
					"receiver_id": receiver_id,
					"payload": message,
					"type_of_transaction": "MESSAGE"
				})
			
			except:
				print("❌ Test Failed ❌")
				exit()

# All tests passed
print("✅ All tests passed ✅")

# Get remaining balance
response = requests.get(address+'/api/get_balance')
print(f'🗃️ The wallet balance (from last validated block is): {response.json().get('balance')}')

# Get remaining temp_balance
response = requests.get(address+'/api/get_temp_balance')
print(f'💵 The temp_balance (from last verified transaction): {response.json().get('temp_balance')}')

# Draw Blockchain