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