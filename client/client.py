from colorama import Fore
import inquirer
import time
import requests
import json
from texttable import Texttable
from utils import utils, drawers

# Opening JSON file
with open('../nodes_config.json') as f:
    nodes_config = json.load(f)
    
#Parse arguments
node = utils.parse_arguments()

# Networking Configuration
address = utils.get_node_address(nodes_config, node)

# Command Line Interface client
def client():
    
	if not utils.check_api_availability(address):
		exit()
	
	#Clear terminal and show brand name
	drawers.clear_terminal()
	drawers.brand()

	while(True):
		menu = [ 
			inquirer.List('menu', 
			message= "BlockChat Client", 
			choices= ['💸 New transaction', '💬 New message', '🎰 Set Stake','📬 Incoming Messages','📋 View all of my transactions','📦 View last block', '🔗 View blockchain', '💰 Show balance', '💁 Help', '🌙 Exit'], 
			),
		]
		choice = inquirer.prompt(menu)['menu']
		drawers.clear_terminal()


		# NEW TRANSACTION CLIENT CALL ======================================== (DONE)
		if choice == '💸 New transaction':
			questions = [
				inquirer.Text(name='receiver', message ='🍀 What is the receiver ID of the lucky one?'),
				inquirer.Text(name='amount', message = '🪙 How many BlockChat coins to send?'),
			]
			answers = inquirer.prompt(questions)
			receiver_id = int(answers['receiver'])
			amount = str(answers['amount'])  
			print('Sending ' + amount + ' BlockChat Coins to client with ID ' + str(receiver_id) + '...')
			try:
				# api client post call  
				response = requests.post(address+'/api/create_transaction', json={
					"receiver_id": receiver_id,
					"payload": amount,
					"type_of_transaction": "COINS"
				})
				
				data = response.json()
				print(data)
			except requests.exceptions.HTTPError:
				if (data):
					print(data)
				else:
					print("Node is not active. Try again later.")
			input("Press any key to go back...")
			drawers.clear_terminal()
			continue


		# NEW MESSAGE CLIENT CALL ======================================== (DONE)
		if choice == '💬 New message':
			questions = [
				inquirer.Text(name='receiver', message ='🍀 What is the Receiver ID of the lucky one?'),
				inquirer.Text(name='message', message = 'What is the message?'),
			]
			answers = inquirer.prompt(questions)
			receiver_id = int(answers['receiver'])
			message = str(answers['message'])  
			print('Sending message: "' + message + '" to client with ID ' + str(receiver_id) + '...')
			try:
				# api client call  for message
				response = requests.post(address+'/api/create_transaction', json={
					"receiver_id": receiver_id,
					"payload": message,
					"type_of_transaction": "MESSAGE"
				})
				
				data = response.json()
				print(data)
			except requests.exceptions.HTTPError:
				if (data):
					print(data)
				else:
					print("Node is not active. Try again later.")
			input("Press any key to go back...")
			drawers.clear_terminal()
			continue


		# SET STAKE CLIENT CALL ======================================== (DONE)
		if choice == '🎰 Set Stake':
			questions = [
				inquirer.Text(name='stake', message ='🎰 How much do you want to stake?'),
			]
			answers = inquirer.prompt(questions)
			stake = str(answers['stake'])

			print('Staking ' + stake + ' BlockChat Coins in order to be in the next lottery...')

			try:
				# api client post to set stake
				response = requests.post(address+'/api/set_stake', json={
					"stake": stake
				})

				data = response.json()
				print(data)
			except requests.exceptions.HTTPError:
				if (data):
					print(data)
				else:
					print("Node is not active. Try again later.")
			input("Press any key to go back...")
			drawers.clear_terminal()
			continue
		
		# INCOMING MESSAGES CLIENT CALL ======================================== (DONE)
		if choice == '📬 Incoming Messages':
			try:
				# api client call to view last block
				chain = requests.get(address+'/api/get_chain')
				chain = chain.json()
				count = 1
				
				print()
				print('📬 Incoming Messages')
				print()
				print(f"{Fore.LIGHTMAGENTA_EX}---------------------{Fore.RESET}")
				# Print incoming messages
				for block in chain:
					for transaction in block['transactions']:
						if transaction['type'] == "Message" and int(transaction['receiver_id']) == int(node):
							print(f"{count}.")
							print()
							print(f"    {Fore.GREEN}FROM: {Fore.RESET}"+transaction['sender_id']+"")
							print(f"    {Fore.LIGHTBLUE_EX}MESSAGE: {Fore.RESET}"+transaction['payload']+"")
							print(f"{Fore.LIGHTMAGENTA_EX}---------------------{Fore.RESET}")
							count += 1
				
			except requests.exceptions.HTTPError:
				print("Node is not active. Try again later.")
			input("Press any key to go back...")
			drawers.clear_terminal()
			continue

		if choice == '📋 View all of my transactions':
			try:
				# api client call to view last block
				response = requests.get(address+'/api/get_transaction_list')
				data = response.json()
				table = Texttable()
				table.add_row(["Sender", "Receiver", "Type", "Message", "Amount", "Nonce", "Transaction ID"])
				for transaction in data["My transactions"]:
					if transaction["type_of_transaction"] == "COINS" and transaction["sender_address"] == "0":
						table.add_row([transaction["sender_address"], transaction["receiver_address"], "STAKE", "None", transaction["amount"], transaction["nonce"], transaction["transaction_id"]])
					elif transaction["type_of_transaction"] == "COINS" or transaction["type_of_transaction"] == "INITIAL":
						table.add_row([transaction["sender_address"], transaction["receiver_address"], transaction["type_of_transaction"],"None", transaction["amount"], transaction["nonce"], transaction["transaction_id"]])
					elif transaction["type_of_transaction"] == "MESSAGE":
						table.add_row([transaction["sender_address"], transaction["receiver_address"], transaction["type_of_transaction"], transaction["message"], transaction["amount"], transaction["nonce"], transaction["transaction_id"]])
				print(table.draw())
			except requests.exceptions.HTTPError:
				print("Node is not active. Try again later.")
			input("Press any key to go back...")
			drawers.clear_terminal()
			continue
		# VIEW LAST BLOCK CLIENT CALL ========================================
		if choice == '📦 View last block':
			try:
				# api client call to view last block
				response = requests.get(address+'/api/view_last_block')
				data = response.json()
				drawers.draw_blockchain(data)
			except requests.exceptions.HTTPError:
				print("Node is not active. Try again later.")
			input("Press any key to go back...")
			drawers.clear_terminal()
			continue

		# VIEW BLOCKCHAIN CLIENT CALL ======================================== (DONE)
		if choice == '🔗 View blockchain':
			try:
				# api client call to view last block
				chain = requests.get(address+'/api/get_chain')
				chain = chain.json()
				#print(chain)
				drawers.draw_blockchain(chain)
			except requests.exceptions.HTTPError:
				print("Node is not active. Try again later.")
			input("Press any key to go back...")
			drawers.clear_terminal()
			continue


		# SHOW BALANCE CLIENT CALL ======================================== (DONE)
		if choice == '💰 Show balance':
			try:
				data = requests.get(address+'/api/get_balance')
				try:
					coins = data.json().get('balance')              
					print(f"Your Balance is: {Fore.GREEN}{coins} BlockChat Coins{Fore.RESET}\n")
				except:
					print("Validated block not available yet. Try again later")
			except requests.exceptions.HTTPError:
				print("Node is not active. Try again later.")
			input("Press any key to go back...")
			drawers.clear_terminal()
			continue

		# HELP =======================================
		if choice == '💁 Help':
			drawers.clear_terminal()
			print('💸 New transaction:')
			print('Send transaction to a node. Select node id and amount.\n\n')

			print('💬 New message:')
			print('Send a message to a node. Select node id and message.\n\n')

			print('🎰 Set Stake:')
			print('Set the stake for the client wallet.\n\n')

			print('📬 Incoming Messages:')
			print('View incoming messages from other nodes.\n\n')

			print('📋 View all of my transactions:')
			print('View all transactions from the client wallet.\n\n')

			print('📦 View last block:')
			print('View the last block in the blockchain.\n\n')
			
			print('🔗 View blockchain:')
			print('A visual representation of the blockchain.\n\n')

			print('💰 Show balance')
			print('View the balance of the client from the client wallet.\n\n')

			input("Press any key to go back...")
			# Go back to main client menu after help
			drawers.clear_terminal()
			# Remove the break statement to go back to the client menu
			continue
		# EXIT =======================================
		if choice == '🌙 Exit':
			drawers.clear_terminal()
			print("We will miss you 💋")
			time.sleep(0.7)
			drawers.clear_terminal()
			break

client()