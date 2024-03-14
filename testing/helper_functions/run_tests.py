import argparse
import os
import re
import requests
import json

# Function that parses the input files from trans0.txt to a list of receiver ids and a list of messages
def parse_input_files(node_number: int):
	receiver_id = []
	message = []
	# Read to the correct trans.txt file according to the node number
	with open('trans'+str(node_number)+'.txt', 'r') as file:
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
					print(f"Transaction id: {receiver_id}")
					# Get message after id and one space after
					current_message = line[match.end():].lstrip()  # Remove the first space from the message
					message.append(current_message)

					# Debugging
					print(f"Message: {message}")
			except requests.exceptions.RequestException as e:
					# Handle exceptions
					print("❌ Parsing Failed ❌")
					print(f"Exception: {e}")
	# All tests passed
	print("✅ Parsing Successful ✅")
	return receiver_id, message


# Function that sends the messages to the receiver from the parsed lists
def send_messages(node_number, receiver_id_list, message_list, address):
	# Opening JSON file
	f = open('../nodes_config.json')
	nodes_config = json.load(f)
	f.close()
	
	# Networking Configuration
	address = nodes_config.get(f'node{node_number}') if node_number in range(10) else print("Invalid node number") and exit()
	
	for i in receiver_id_list:
		# Get the receiver id
		receiver_id = receiver_id_list[receiver_id_list.index(i)]
		# Get the message
		message = message_list[receiver_id_list.index(i)]

		# Debugging
		print(f"Sending message to {receiver_id} with message: {message}")
	
		# Send the message to the receiver
		try:
			# api client call  for message
			response = requests.post(address+'/api/create_transaction', json={
				"receiver_id": receiver_id,
				"payload": message,
				"type_of_transaction": "MESSAGE"
			})
	
			# Check if the status code is not 200 OK
			if response.status_code != requests.codes.ok:
				# If the status code is not OK, raise an exception
				response.raise_for_status()
		except requests.exceptions.RequestException as e:
			# Handle exceptions
			print("❌ Sending Messages Failed ❌")
			print(f"Exception: {e}")
	
	# All tests passed
	print("✅ Messages were send successfully ✅")
	return True