import json
from dotenv import load_dotenv
import os

from time import time
from Crypto.Hash import SHA256

from transaction import Transaction
from blockchain import Blockchain

#load_dotenv()
#block_size = int(os.getenv('BLOCK_SIZE'))
#mining_difficulty = int(os.getenv('MINING_DIFFICULTY'))

class Block:
    def __init__(self, previous_hash, validator):
        #Initialize a block
        self.index = None
        self.timestamp = time()
        self.transactions = []
        self.validator = validator
        self.previous_hash = previous_hash
        self.current_hash = self.calculate_hash() 
	
    def calculate_hash(self):
        #Return hash of the block
        block_object = {
            'timestamp': self.timestamp, 
            'transactions': [tr.transaction_id for tr in self.transactions],
            'previous_hash': self.previous_hash
        }
        
        block_dump = json.dumps(block_object.__str__())
        self.current_hash = SHA256.new(block_dump.encode("ISO-8859-2")).hexdigest()
        
        return self.current_hash
    
    
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
        