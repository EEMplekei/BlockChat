import requests
import time

successful_transactions = 0
def send_messages(address: str, receiver_id_list, message_list):
	global successful_transactions
	for receiver_id, message in zip(receiver_id_list, message_list):
		#time.sleep(1)
		# Debugging
		# print(f"Sending message to {receiver_id} with message: {message}")
		
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
				response.raise_for_status()
			else:
				successful_transactions += 1
		except requests.exceptions.RequestException as e:
			# Handle exceptions
			print("❌ Sending Messages Failed ❌")
			print(f"Exception: {e}")
			return False
		
	# All tests passed
	print(f"✅ Messages were send successfully for Node with address: {address}✅")
	return True