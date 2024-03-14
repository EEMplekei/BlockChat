import re

# Function that parses the input files from trans0.txt to a list of receiver ids and a list of messages
def parse_input_files(node_number: int):
	receiver_id = []
	message = []
	# Read to the correct trans.txt file according to the node number
	with open('../test_inputs/trans'+str(node_number)+'.txt', 'r') as file:
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
					print(f"Transaction id: {current_receiver_id}")
					# Get message after id and one space after
					current_message = line[match.end():].lstrip()  # Remove the first space from the message
					message.append(current_message)

					# Debugging
					print(f"Message: {current_message}")
			except re.error as e:
					# Handle exceptions
					print("❌ Parsing Failed ❌")
					print(f"Exception: {e}")
	# All tests passed
	print("✅ Parsing Successful ✅")
	return receiver_id, message