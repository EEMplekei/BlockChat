from dotenv import load_dotenv
from colorama import Fore
import os

#Load environment variables
load_dotenv()

def try_load_env(env_var: str):
	try:
		value = os.getenv(env_var)
  
	except Exception as e:
		print(f"{Fore.RED}Error loading environment variables: {e}{Fore.RESET}")
		raise e
	return value

# Initialize environment variables
try:
	TOTAL_NODES = int(try_load_env('TOTAL_NODES'))
	FEE_RATE = float(try_load_env('FEE_RATE'))
	BLOCK_SIZE = int(try_load_env('BLOCK_SIZE'))
	INTERNAL_CIDR = try_load_env('INTERNAL_CIDR')
	BOOTSTRAP_IP = try_load_env('BOOTSTRAP_IP')
	BOOTSTRAP_PORT = try_load_env('BOOTSTRAP_PORT') 
except ValueError as e:
	print(f"{Fore.YELLOW}env_variables{Fore.RESET}: {Fore.RED} cannot get environment variables{e}{Fore.RESET}")
	exit(1)