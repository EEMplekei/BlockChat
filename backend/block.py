from time import time
from hashlib import sha256
from blockchain import Blockchain

class Block:
	def __init__(self, previous_hash, validator):
		
		#Initialize a block
		self.index = None
		self.timestamp = time()
		self.transactions = []
		self.validator = validator
		self.previous_hash = previous_hash
		self.current_hash = self.calculate_hash() 
	
	#Hash function calculation
	def calculate_hash(self):
			   
		data_to_hash = ''.join([
			str(self.timestamp),
			''.join(str(tr['transaction_id']) for tr in self.transactions),
			str(self.previous_hash)
		])
		
		return sha256.new(data_to_hash.encode()).hexdigest()	
	
	#Todo
	def validate_block(self, blockchain: Blockchain):
		# Validate current_hash and previous_hash
		# Called from a node when it receives a broadcasted block (that isn't the genesis block)
		# Checks 1)if validator is correct
		#        2)if the previous_hash field is equal to the the hash of the actual previous block
		
		# Special case: If it is the genesis block, it's valid 
		if (self.previous_hash == 1 and self.nonce == 0):
			return True
		
		# Get last block of the chain and check its hash
		prev_block = blockchain.chain[-1]
		
		# 1) Check if the previous_hash field is equal to the the hash of the actual previous block
		if ((self.previous_hash != prev_block.hash)):
			print("❌ Error in block validation: Not correct previous_hash")
			return False

		# 2) Check if validator is correct
		if ():
			print('Block validated !')
			return True
		else:
			print("❌ Error in block validation: Not correct hash")
			return False
		