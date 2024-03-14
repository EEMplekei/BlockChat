from argparse import ArgumentParser
from colorama import Fore
import requests

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
    if node in map(str, range(10)):
        address = nodes_config.get(f'node{node}', lambda: (print("Invalid node number") or exit()))
    else:
        print(f"{Fore.YELLOW}get_node_address{Fore.RESET}: {Fore.RED}Invalid node number{Fore.RESET}")
        exit()
    return address

#Check if the API is available
def check_api_availability(address):
    try:
        response = requests.get(address+'/api/')
        response.raise_for_status()
        if not response.status_code == 200:
            print("❌ API is not available. Try again later ❌")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API on node with address {address} is not available. Try again later ❌")
        return False
    
    return True


