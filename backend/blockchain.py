from dotenv import load_dotenv
import requests
import pickle
import os
from collections import deque

load_dotenv()
block_size = int(os.getenv('BLOCK_SIZE'))

class Blockchain:
    # Blockchain class
    def __init__(self):
        # Initialize a Blockchain
        # chain:                  List of blocks in the original blockchain
        # difficulty:             Number of 0s in block needed for correct nonce to be found
        # maxBlockTransactions    Capacity of a single block
        # UTXOs                   List of deques containing the UTXOs for all nodes in the cluster
        # trxs                    Set of transaction hashes in the original blockhain (to avoid double transactions)
        self.chain = [] # list<Block>
        self.difficulty = mining_difficulty
        self.maxBlockTransactions = block_size
        self.UTXOs = []
        self.trxns = set()
    
    # Validate the chain from the bootstrap node
    def validate_chain(self):
        for i in range(0, len(self.chain)-1):
            temp_block = self.chain[i]
            if (not (i==0 and temp_block.previous_hash == 1 and temp_block.nonce == 0)):
                    return False
            elif(not temp_block.validate_block(self)):
                 return False
        return True

    # Get the total wallet balance (based on the wallet of specific client_id)
    def wallet_balance(self, client_id):      
        balance = 0
        for utxo in self.UTXOs[client_id]:
             balance += utxo.amount

        return balance