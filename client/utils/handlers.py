from colorama import Fore, Style
from texttable import Texttable
import requests
import inquirer
from utils import drawers

def handle_new_transaction(address):
	
	questions = [
				inquirer.Text(name='receiver', message ='🍀 What is the receiver ID of the lucky one?'),
				inquirer.Text(name='amount', message = '🪙 How many BlockChat coins to send?'),
			]
	answers = inquirer.prompt(questions)
	
	#Input checking for receiver and amount
	try:
		receiver_id = int(answers['receiver'])
		if receiver_id < 0:
			raise ValueError
	except ValueError:
		print("Invalid receiver ID")
		input("Press any key to go back...")
		drawers.clear_terminal()
		return

	try:
		amount = int(answers['amount'])
		if amount <= 0:
			raise ValueError
	except ValueError:
		print("Invalid amount")
		input("Press any key to go back...")
		drawers.clear_terminal()
		return

	print('Sending ' + str(amount) + ' BlockChat Coins to client with ID ' + str(receiver_id) + '...')
 
	try:
		# api client post call  
		response = requests.post(address+'/api/create_transaction', json={
			"receiver_id": receiver_id,
			"payload": str(amount),
			"type_of_transaction": "COINS"
		})
  
		if response.status_code == 200:
			print(f"{Fore.GREEN}Coins sent successfully{Fore.RESET}")
		data = response.json()
  
	except requests.exceptions.HTTPError:
		if (data):
			print(f"{Fore.LIGHTRED_EX}{data}{Fore.RESET}")
   
		else:
			print(f"{Fore.LIGHTRED_EX}Node is not active. Try again later.{Fore.RESET}")
	input("Press any key to go back...")
	drawers.clear_terminal()

def handle_new_message(address):
	questions = [
		inquirer.Text(name='receiver', message ='🍀 What is the Receiver ID of the lucky one?'),
		inquirer.Text(name='message', message = 'What is the message?'),
	]
	answers = inquirer.prompt(questions)

	#Input checking for receiver and message
	try:
		receiver_id = int(answers['receiver'])
		if receiver_id < 0:
			raise ValueError
	except ValueError:
		print("Invalid receiver ID")
		input("Press any key to go back...")
		drawers.clear_terminal()
		return

	message = str(answers['message'])
	print('Sending message: "' + message + '" to client with ID ' + str(receiver_id) + '...')
	try:
		# api client call for message
		response = requests.post(address+'/api/create_transaction', json={
			"receiver_id": receiver_id,
			"payload": message,
			"type_of_transaction": "MESSAGE"
		})
		data = response.json()

		if response.status_code == 200:
			print(f"{Fore.GREEN}Message sent successfully!{Fore.RESET}")
		else:
			print(f"{Fore.LIGHTRED_EX}{data}{Fore.RESET}")
		
	except requests.exceptions.HTTPError:
		if (data):
			print(f"{Fore.LIGHTRED_EX}{data}{Fore.RESET}")
		else:
			print(f"{Fore.LIGHTRED_EX}Node is not active. Try again later.{Fore.RESET}")
	input("Press any key to go back...")
	drawers.clear_terminal()
		
def handle_new_stake(address):
	questions = [
		inquirer.Text(name='stake', message ='🎰 How much do you want to stake?'),
		]
	answers = inquirer.prompt(questions)
 
	#Input checking for stake
	try:
		stake = int(answers['stake'])
		if stake < 0:
			raise ValueError
	except ValueError:
		print("Invalid stake")
		input("Press any key to go back...")
		drawers.clear_terminal()
		return

	print('Staking ' + str(stake) + ' BlockChat Coins in order to be in the next lottery...')

	try:
		# api client post to set stake
		response = requests.post(address+'/api/set_stake', json={
			"stake": str(stake)
		})

		if response.status_code == 200:
			print(f"{Fore.GREEN}Stake set successfully!{Fore.RESET}")
		else:
			data = response.json()
			print(data)
	except requests.exceptions.HTTPError:
		if (data):
			print(f"{Fore.LIGHTRED_EX}{data}{Fore.RESET}")
		else:
			print(f"{Fore.LIGHTRED_EX}Node is not active. Try again later.{Fore.RESET}")
	input("Press any key to go back...")
	drawers.clear_terminal()
	
def handle_view_incoming_messages(address, node):
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
				if transaction['type'] == "Message" and str(transaction['receiver_id']) == str(node):
					print(f"{count}.")
					print()
					print(f"    {Fore.GREEN}FROM: {Fore.RESET}"+transaction['sender_id']+"")
					print(f"    {Fore.LIGHTBLUE_EX}MESSAGE: {Fore.RESET}"+transaction['payload']+"")
					print(f"{Fore.LIGHTMAGENTA_EX}---------------------{Fore.RESET}")
					count += 1
			
	except requests.exceptions.HTTPError:
		print(f"{Fore.LIGHTRED_EX}Node is not active. Try again later.{Fore.RESET}")
	input("Press any key to go back...")
	drawers.clear_terminal()
 
def handle_view_all_transactions(address):	
	try:
		# api client call to view last block
		response = requests.get(address+'/api/get_wallet_transaction_list')
		data = response.json()
		table = Texttable()
		table.add_row(["Sender", "Receiver", "Type", "Message", "Amount", "Nonce", "Transaction ID"])
		for transaction in data["Wallet transactions"]:
			if transaction["type_of_transaction"] == "COINS" or transaction["type_of_transaction"] == "INITIAL":
				table.add_row([transaction["sender_address"], transaction["receiver_address"], transaction["type_of_transaction"],"None", transaction["amount"], transaction["nonce"], transaction["transaction_id"]])
			elif transaction["type_of_transaction"] == "MESSAGE":
				table.add_row([transaction["sender_address"], transaction["receiver_address"], transaction["type_of_transaction"], transaction["message"], transaction["amount"], transaction["nonce"], transaction["transaction_id"]])
			elif transaction["type_of_transaction"] == "STAKE":
				table.add_row([transaction["sender_address"], 0, "STAKE", "None", transaction["amount"], transaction["nonce"], transaction["transaction_id"]])
		print(table.draw())
	except requests.exceptions.HTTPError:
		print(f"{Fore.LIGHTRED_EX}Node is not active. Try again later.{Fore.RESET}")
	input("Press any key to go back...")
	drawers.clear_terminal()

def handle_view_last_block(address):
	try:
		# api client call to view last block
		response = requests.get(address+'/api/view_last_block')
		data = response.json()
  
		drawers.brand()
		print("\n    ⛓️  BlockChat Last Block  ⛓️\n")
		drawers.draw_block(data[0])
		print()
	except requests.exceptions.HTTPError:
		print(f"{Fore.LIGHTRED_EX}Node is not active. Try again later.{Fore.RESET}")
	input("Press any key to go back...")
	drawers.clear_terminal()

def handle_view_blockchain(address):
	try:
		# api client call to view last block
		chain = requests.get(address+'/api/get_chain')
		chain = chain.json()
		#print(chain)
		drawers.draw_blockchain(chain)
	except requests.exceptions.HTTPError:
		print(f"{Fore.LIGHTRED_EX}Node is not active. Try again later.{Fore.RESET}")
	input("Press any key to go back...")
	drawers.clear_terminal()
 
def handle_show_balance(address):
	try:
		data = requests.get(address+'/api/get_balance')
		try:
			coins = data.json().get('balance')              
			print(f"Your Balance is: {Fore.GREEN}{Style.BRIGHT}{coins} BlockChat Coins{Style.NORMAL}{Fore.RESET}\n")
		except:
			print("Validated block not available yet. Try again later")
	except requests.exceptions.HTTPError:
		print(f"{Fore.LIGHTRED_EX}Node is not active. Try again later.{Fore.RESET}")
	input("Press any key to go back...")
	drawers.clear_terminal()

def show_help():
	drawers.clear_terminal()
	print(f'{Style.BRIGHT}💸 New transaction:{Style.NORMAL}')
	print('Send transaction to a node. Select node id and amount.\n\n')

	print(f'{Style.BRIGHT}💬 New message:{Style.NORMAL}')
	print('Send a message to a node. Select node id and message.\n\n')

	print(f'{Style.BRIGHT}🎰 Set Stake:{Style.NORMAL}')
	print(f'''Set the stake for the client wallet.{Fore.CYAN}
    This is stake will be frozen from your account from now on and will be used in the PoS algorithm.
    You can change it anytime using a different value. Use 0 to set to zero and not take part in the PoS algorithm.{Fore.RESET}\n''')
    
	print(f'{Style.BRIGHT}📬 Incoming Messages:{Style.NORMAL}')
	print('View incoming messages from other nodes.\n\n')

	print(f'{Style.BRIGHT}📋 View all of my transactions:{Style.NORMAL}')
	print('View all transactions from the client wallet.\n\n')

	print(f'{Style.BRIGHT}📦 View last block:{Style.NORMAL}')
	print('View the last block in the blockchain.\n\n')
	
	print(f'{Style.BRIGHT}🔗 View blockchain:{Style.NORMAL}')
	print('A visual representation of the blockchain.\n\n')

	print(f'{Style.BRIGHT}💰 Show balance:{Style.NORMAL}')
	print('View the balance of the client from the client wallet.\n\n')

	input("Press any key to go back...")
	# Go back to main client menu after help
	drawers.clear_terminal()
	# Remove the break statement to go back to the client menu
