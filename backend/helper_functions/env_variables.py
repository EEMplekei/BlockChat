import os
from colorama import Fore

def try_load_env(env_var: str):
	try:
		value = int(os.getenv(env_var))
  
	except Exception as e:
		print(f"{Fore.RED}Error loading environment variables: {e}{Fore.RESET}")
		raise e
	return value