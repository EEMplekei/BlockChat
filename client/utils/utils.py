from argparse import ArgumentParser
from colorama import Fore, Style
from utils import drawers
from utils import handlers
import json
import requests
import inquirer
import time

def get_nodes_config():
    # Opening JSON file
	with open('../nodes_config.json') as f:
		try:
			nodes_config = json.load(f)
		except json.JSONDecodeError:
			print(f"{Fore.RED}Error: nodes_config.json is not a valid JSON file{Fore.RESET}")
			exit()
	return nodes_config

#Parse command line arguments
def parse_arguments():
	try:
		arg_parser = ArgumentParser()
		arg_parser.add_argument("-n", "--node", help="Node you want to connect to", required = True)
		args = arg_parser.parse_args()
		return args.node
	except Exception as e:
		print(f"{Fore.YELLOW}parse_arguments: {Fore.RED}{e}{Fore.RESET}")
		exit(-1)

#Get the address of the node
def get_node_address(nodes_config, node):
	try:
		return nodes_config[node]
	except KeyError:
		print(f"{Fore.YELLOW}get_node_address{Fore.RESET}: {Fore.RED}Invalid node{Fore.RESET}")
		exit()
	# if node in map(str, range(10)):
	# 	print(nodes_config)
	# 	address = nodes_config.get(f'{node}', lambda: (print("Invalid node") or exit()))
	# else:
	# 	print(f"{Fore.YELLOW}get_node_address{Fore.RESET}: {Fore.RED}Invalid node{Fore.RESET}")
	# 	exit()
	# return address

#Check if the API is available
def check_api_availability(address, node):
	try:
		response = requests.get(address+'/api/')
		response.raise_for_status()
		if not response.status_code == 200:
			print("❌ API is not available. Try again later ❌")
			return False
	except requests.exceptions.RequestException as e:
		print(f"❌ API on {Style.BRIGHT}{node}{Style.NORMAL} with address {Style.BRIGHT}{address}{Style.NORMAL} is not available. Try again later ❌")
		return False
	
	return True

def get_user_choice(node):
	menu = [
		inquirer.List(
			'menu',
			message=f"{Fore.LIGHTBLUE_EX}BlockChat Client [{Fore.CYAN}{Style.BRIGHT}Node {node}{Style.RESET_ALL}{Fore.LIGHTBLUE_EX}]{Fore.RESET}", 
			choices=[
				'💸 New transaction', 
				'💬 New message', 
				'🎰 Set Stake',
				'📬 Incoming Messages',
				'📋 View all of my transactions',
				'📦 View last block', 
				'🔗 View blockchain', 
				'💰 Show balance', 
				'💁 Help', 
				'🌙 Exit'
			],
			carousel= True
		),
	]
	choice = inquirer.prompt(menu)['menu']
	return choice

def handle_user_choice(choice, address, node):
	if choice == '💸 New transaction':
		handlers.handle_new_transaction(address)

	elif choice == '💬 New message':
		handlers.handle_new_message(address)

	elif choice == '🎰 Set Stake':
		handlers.handle_new_stake(address)
	
	elif choice == '📬 Incoming Messages':
		handlers.handle_view_incoming_messages(address, node)

	elif choice == '📋 View all of my transactions':
		handlers.handle_view_all_transactions(address)

	# VIEW LAST BLOCK CLIENT CALL ========================================
	elif choice == '📦 View last block':
		handlers.handle_view_last_block(address)

	# VIEW BLOCKCHAIN CLIENT CALL ======================================== (DONE)
	elif choice == '🔗 View blockchain':
		handlers.handle_view_blockchain(address)

	# SHOW BALANCE CLIENT CALL ======================================== (DONE)
	elif choice == '💰 Show balance':
		handlers.handle_show_balance(address)
  		
	# HELP =======================================
	elif choice == '💁 Help':
		handlers.show_help()

	# EXIT =======================================
	elif choice == '🌙 Exit':
		drawers.clear_terminal()
		print("We will miss you 💋")
		time.sleep(0.7)
		drawers.clear_terminal()
		exit()
