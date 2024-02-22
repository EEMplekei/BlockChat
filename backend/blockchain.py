from dotenv import load_dotenv
import requests
import pickle
import os
from collections import deque

load_dotenv()
block_size = int(os.getenv('BLOCK_SIZE'))
mining_difficulty = int(os.getenv('MINING_DIFFICULTY'))

class Blockchain:
    def __init__(self):
        """
        Initialize a Blockchain
        chain:                  List of blocks in the original blockchain
        maxBlockTransactions    Capacity of a single block
        UTXOs                   List of deques containing the UTXOs for all nodes in the cluster
        trxs                    Set of transaction hashes in the original blockhain (to avoid double transactions)
        """
        self.chain = [] # list<Block>
        self.maxBlockTransactions = block_size
        self.UTXOs = []
        self.trxns = set()
        
    def validate_chain(self):
        """
        Validate the chain from the bootstrap node
        """
        for i in range(0, len(self.chain)-1):
            temp_block = self.chain[i]
            # check if it is the genesis block
            if (not (i==0 and temp_block.previous_hash == 1 and temp_block.nonce == 0)):
                    return False
            elif(not temp_block.validate_block(self)):
                 return False
        return True
    