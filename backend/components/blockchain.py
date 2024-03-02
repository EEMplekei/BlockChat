import os
from colorama import Fore
from dotenv import load_dotenv

try:
	load_dotenv("../.env")
	block_size = int(os.getenv('BLOCK_SIZE'))
except Exception as e:
	#Either there is no such env var so we get None or it is not int castable
	print(f"{Fore.RED}Cannot get BLOCK_SIZE from environment variable: {e}{Fore.RESET}")
	print(f"{Fore.YELLOW}Using default block size of 10{Fore.RESET}")
	block_size = 10

# Blockchain class 
class Blockchain:
	
	chain = list()
	block_capacity : int = None
	transactions_hashes = set()
 
	# Initialize a Blockchain
	def __init__(self):
		
		self.chain = [] 						# List of blocks in the blockchain (list<block>)
		self.block_capacity = block_size  		# Capacity of a single block
		self.transactions_hashes = set()		# Set of transaction hashes in the original blockchain (to avoid double transactions)
	
	# Validate the chain from the bootstrap node
	def validate_chain(self):
	
		# Check if the chain is empty and then validate the genesis block
		if self.chain:
			genesis_block = self.chain[0]
			if genesis_block.previous_hash != 1 or genesis_block.validator != 0:
				print(f"{Fore.RED}Cannot validate the chain: Genesis block is not valid {Fore.RESET}")
				return False

		#Validate other blocks
		for index, block in enumerate(self.chain):
			if not block.validate_block(self):
				print(f"{Fore.RED}Cannot validate the chain: Block with hash \"{block.hash}\" and index \"{index}\" is not valid{Fore.RESET}")
				return False

		return True