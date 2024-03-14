import requests
import json

# Function that stakes the amount of coins on the node
def initial_stake(node_number: int, stake_amount: int):
	# Opening JSON file
	f = open('../../nodes_config.json')
	nodes_config = json.load(f)
	f.close()

	try:
		# Networking Configuration
		address = nodes_config.get(f'node{node_number}') if node_number in range(10) else print("Invalid node number") and exit()

		# api client call  for staking
		response = requests.post(address+'/api/set_stake', json={
			"stake": stake_amount
		})

	except requests.exceptions.RequestException as e:
		# Check if the status code is not 200 OK
		if response.status_code != requests.codes.ok:
			# If the status code is not OK, raise an exception
			print("❌ Staking Failed ❌")
			response.raise_for_status()
	
	# All tests passed
	print("✅ Staking Successful ✅")
	return True