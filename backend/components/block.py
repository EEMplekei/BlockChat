from time import time
from hashlib import sha256
from colorama import Fore
from components.transaction import TransactionType

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
	
	#Validate a block (check correct validator, check previous hash is correct, validate current hash)
	#We assume this function does not get called on the genesis block (to avoid excessive if statements that will fail on every other on the blocks)
	def validate_block(self, prev_hash, validator: int):
				
		#Check validator and previous hash
		if (validator != self.validator) or (self.previous_hash != prev_hash):
			return False
		
		#Rehash block and check it's hash
		if (self.calculate_hash() != self.hash):
			return False

		return True

	#Get the transactions from a block
	def get_transactions_from_block(self, node):
		transactions = []

		for transaction in self.transactions:
			if transaction.receiver_address == 0:
				transactions.append({
					"type": "Stake",
					"sender_id": node.ring[str(transaction.sender_address)]['id'],
					"amount": transaction.amount
				})
			else:
				if(transaction.type_of_transaction == TransactionType.COINS):
					transactions.append({
					"type": "Coins Transfer",
					"sender_id": node.ring[str(transaction.sender_address)]['id'],
					"receiver_id": node.ring[str(transaction.receiver_address)]['id'],
					"amount": transaction.amount
					})
				elif (transaction.type_of_transaction == TransactionType.MESSAGE):
					transactions.append({
					"type": "Message",
					"sender_id": node.ring[str(transaction.sender_address)]['id'],
					"receiver_id": node.ring[str(transaction.receiver_address)]['id'],
					"message": transaction.message
					})
				else:
					print(f"{Fore.RED}Panic! Invalid transaction type found in block!{Fore.RESET}")
					raise ValueError("Invalid transaction type found in block")
		return transactions
