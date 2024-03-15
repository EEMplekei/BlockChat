import requests

# Function that stakes the amount of coins on the node
def initial_stake(address: str, stake_amount: int):
	try:
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