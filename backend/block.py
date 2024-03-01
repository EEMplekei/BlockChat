from time import time
from hashlib import sha256
from blockchain import Blockchain

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
			''.join(str(tr['transaction_id']) for tr in self.transactions),
			str(self.previous_hash)
		])
		
		self.hash = sha256.new(data_to_hash.encode()).hexdigest()	
	
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