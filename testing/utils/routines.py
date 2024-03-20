from colorama import Fore, Style
from sys import platform
from time import sleep
import requests
import subprocess

# Run something (e.g. a bash script) on each node to start the API
def setup_nodes(nodes, block_size):
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Setting up the nodes{Fore.RESET}{Style.NORMAL}\n")
	global proc
		
	#If running in Linux run the first script else the MacOS script, suppress output
	if platform == "linux":
		script_path = ['bash', '../deploy/execute_okeanos_gnome.sh', str(len(nodes)), str(block_size)]
	elif platform == "darwin":
		script_path = ['bash', '../deploy/execute_okeanos_gnome.sh', str(len(nodes)), str(block_size)]
	else :
		print(f"	{Fore.LIGHTRED_EX}Unsupported OS, start nodes one you own{Fore.RESET}")
  
	proc = subprocess.Popen(script_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Test if all the nodes are running to continue with benchmarking
	test_all_nodes_are_up(nodes)

# This function checks if all nodes are up, one by one until all are up, take your time to set them up
# When all are up it returns
def test_all_nodes_are_up(nodes):
	
	#Check if the API is available
	def check_api_availability(address):
		try:
			response = requests.get(address+'/api/')
			response.raise_for_status()
			if not response.status_code == 200:
				return False
		except requests.exceptions.RequestException:
			return False
		return True

	for node, address in nodes.items():
		while not check_api_availability(address):
			continue
		print(f"	{Fore.CYAN}Node {Style.BRIGHT}{node}{Style.NORMAL} is up and running{Fore.RESET}")

	#Now we have to wait for the bootstrap to send the the ring, blockchain and the initial transactions
	sleep(1)
	print(f"\n	{Fore.GREEN}All nodes are up and running{Fore.RESET}\n")

def set_initial_stake(nodes, stake : int):
	print(f"{Fore.GREEN}{Style.BRIGHT}➜ Setting the initial stake on the nodes{Fore.RESET}{Style.NORMAL}\n")
	
	for node, address in nodes.items():
		try:
			# api client post call
			response = requests.post(address+'/api/set_stake', json={
				"stake": stake
			})
			data = response.json()
			print(f"	{Fore.LIGHTCYAN_EX}Node {Style.BRIGHT}{node}{Style.NORMAL} has set the initial stake{Fore.RESET}")
		except requests.exceptions.HTTPError:
			print(f"	{Fore.RED}{Style.BRIGHT}Node {node} has failed to set the initial stake{Fore.RED}{Style.NORMAL}")
			exit(-4)
		except requests.exceptions.ConnectionError:
			print(f"	{Fore.RED}Node {Style.BRIGHT}{node}{Style.NORMAL} with address {Style.BRIGHT}{address}{Style.NORMAL} seems to be down{Fore.RED}")
			exit(-5)
	print(f"\n	{Fore.GREEN}Initial Stake Set{Fore.RESET}\n")
