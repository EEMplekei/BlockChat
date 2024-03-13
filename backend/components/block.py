from time import time
from hashlib import sha256
from colorama import Fore
from components.transaction import TransactionType
from helper_functions.env_variables import FEE_RATE

class Block:
	
	timestamp = None
	transactions = list()
	validator = None
	previous_hash = None
	hash = None
	
	def __init__(self, previous_hash, validator):
		
		#Initialize a block
		self.timestamp = time()
		self.transactions = []
		self.validator = validator
		self.previous_hash = previous_hash
		self.hash = None
	
		# Note: By not using calculate hash to auto calculate and assign the hash on constructor calling,
		# on network arrival, create an instance of it with the posted fields and then check that the hash that WE calculate
		# is the same as the one sent
  
	#Hash function calculation
	def calculate_hash(self):
			   
		data_to_hash = ''.join([
			str(self.timestamp),
			''.join(str(tr.transaction_id) for tr in self.transactions),
			str(self.previous_hash)
		])
		
		self.hash = sha256(data_to_hash.encode()).hexdigest()
		return self.hash
	
	#Validate a block (check correct validator, check previous hash is correct, validate current hash)
	#We assume this function does not get called on the genesis block (to avoid excessive if statements that will fail on every other on the blocks)
	def validate_block(self, prev_hash, validator: int):
		#Check validator and previous hash
		if (self.previous_hash != prev_hash):
			print(f"{Fore.RED}Attention! Block validation failed --> Previous Hash is not accurate !{Fore.RESET}")
			print(f"{Fore.RED}Actual Validator Hash: {self.previous_hash} | Given Hash: {prev_hash}{Fore.RESET}")
			return False
		if (str(validator) != str(self.validator)):
			print(f"{Fore.RED}Attention! Block validation failed --> Validator pk is not accurate !{Fore.RESET}")
			print(f"{Fore.RED}Actual Validator pk: {self.validator} | Given pk: {validator}{Fore.RESET}")
			return False
		
		#Rehash block and check it's hash
		if (self.calculate_hash() != self.hash):
			print(f"{Fore.RED}Attention! Block validation failed --> Hash is not accurate !{Fore.RESET}")
			print(f"{Fore.RED}Actual Hash: {self.hash} | Given Hash: {self.calculate_hash()}{Fore.RESET}")
			return False

		print(f"{Fore.GREEN}Block validation passed!{Fore.RESET}")
		return True

	# Get total amount of fees from a block 
	def get_total_fees(self): 
		# Initialize total_fees 
		total_fees = 0 
		for transaction in self.transactions: 
			if transaction.type_of_transaction == TransactionType.COINS: 
				total_fees += (transaction.amount)*FEE_RATE 
		
		return total_fees

	#Get the transactions from a block
	def get_transactions_from_block(self, node):

		#Special case for the genesis block
		if self.previous_hash == 1:
			return self.get_genesis_block_transactions(node)

		#General case for any other block
		transactions = []
		for transaction in self.transactions:
			if transaction.receiver_address == 0:
				transactions.append({
					"type": "Stake",
					"sender_id": str(node.ring[str(transaction.sender_address)]['id']),
					"receiver_id": "0",
					"payload": str(transaction.amount)
				})
			else:
				if(transaction.type_of_transaction == TransactionType.INITIAL):
					transactions.append({
					"type": "Initial Transaction",
					"sender_id": str(node.ring[str(transaction.sender_address)]['id']),
					"receiver_id": str(node.ring[str(transaction.receiver_address)]['id']),
					"payload": str(transaction.amount)
					})
				elif(transaction.type_of_transaction == TransactionType.COINS):
					transactions.append({
					"type": "Coins Transfer",
					"sender_id": str(node.ring[str(transaction.sender_address)]['id']),
					"receiver_id": str(node.ring[str(transaction.receiver_address)]['id']),
					"payload": str(transaction.amount)
					})
				elif (transaction.type_of_transaction == TransactionType.MESSAGE):
					transactions.append({
					"type": "Message",
					"sender_id": str(node.ring[str(transaction.sender_address)]['id']),
					"receiver_id": str(node.ring[str(transaction.receiver_address)]['id']),
					"payload": transaction.message
					})
				else:
					print(f"{Fore.YELLOW} get_transactions_from_block{Fore.RESET}:{Fore.RED}Invalid transaction type found in block!{Fore.RESET}")
					raise ValueError("Invalid transaction type found in block")
		return transactions

	def get_genesis_block_transactions(self, node):
		transactions = []

		for transaction in self.transactions:
			#print(transaction.sender_address, transaction.receiver_address, transaction.amount, transaction.type_of_transaction)
			if transaction.sender_address == '0':
				transactions.append({
					"type": "Genesis",
					"receiver_id": str(node.ring[str(transaction.receiver_address)]['id']),
					"sender_id": "-",
					"payload": str(transaction.amount)
				})
			else:
				print(f"{Fore.YELLOW}get_genesis_block_transactions{Fore.RESET}: {Fore.RED}Invalid transaction type found in genesis block!{Fore.RESET}")
				raise ValueError("Invalid transaction type found in genesis block")
		return transactions