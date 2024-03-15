import requests

# Function that sends the messages to the receiver from the parsed lists ON ONE NODE!
def send_messages(address: str, receiver_id_list, message_list):
	for i in receiver_id_list:
		# Get the receiver id
		receiver_id = receiver_id_list[receiver_id_list.index(i)]
		# Get the message
		message = message_list[receiver_id_list.index(i)]

		# Debugging
		#print(f"Sending message to {receiver_id} with message: {message}")
	
		# Send the message to the receiver
		try:
			# api client call  for message
			response = requests.post(address+'/api/create_transaction', json={
				"receiver_id": int(receiver_id),
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
			return False
	
	# All tests passed
	print(f"✅ Messages were send successfully for Node with address: {address}✅")
	return True