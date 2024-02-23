# NODE 
## Responsible for creating and populating new blocks

# Listens for new transactions
# Create a new Block if previous is full
# Begin mining if Block is full
# Stop mining if new Block get verified
# Begin mining of next block

# !! Each time you try to mine a block you create
# a temp version of all UTXOs. When a new block gets mined
# you discard the temp version and update the original UTXOs 
# database with the UTXOs derived from the mined block's transactions
# !! In case of conflict, get the UTXOs from the node with the longest chain

from collections import deque
from copy import deepcopy
from dotenv import load_dotenv
import requests
import pickle
import json
import os
import random
import threading

from dump import Dump

from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction
from block import Block
from utxo import UTXO


load_dotenv()
block_size = int(os.getenv('BLOCK_SIZE'))

class Node:

    def __init__(self):
        
        # wallet:     Contains the wallet of each node
        #             Also contains the private key, public key == address
        # ip:         IP of the node
        # port:       Port of the service the node listens to
        # id:         A number that denotes the name of the node in the cluster
        # ring:       A list of all the nodes in the cluster
        # blockchain: A blockchain instance from the node's perspective
        # is_bootstrap:   True if the current node is the Bootstrap node
        # current_block:  The block that lefts to be filled with transactions
        # pending_blocks: All the blocks that are filled with transactions but are not yet mined
        # incoming_block: True if there has been received another mined
        # processing_block: True if there is a new incoming block waiting to get validated (used in api.py)
        # pending_transactions:  List of transactions destined to be mined
        # temp_utxos:     (for validation) Temporary snapshot of UTXOs that is used for the currently mined block
        
        # incoming_block_lock:    Lock for incoming_block variable
        # processing_block_lock:  Lock for processing_block variable
        
        self.wallet = Wallet() # create_wallet
        self.ip = None
        self.port = None
        self.id = None
        self.ring = {}     # address: {id, ip, port, balance}
        self.blockchain = Blockchain()
        self.is_bootstrap = False
        self.current_block = None
        self.incoming_block = False
        self.processing_block = False
        self.pending_transactions = deque()
        self.temp_utxos = None  # for validation purposes

        self.incoming_block_lock = threading.Lock()
        self.processing_block_lock = threading.Lock()

        self.dump = Dump()


    def create_new_block(self):
        #Creates a new block for the blockchain
        previous_hash = None
        # Special case for GENESIS block
        if (len(self.blockchain.chain) == 0):
            previous_hash = 1
            
        self.current_block = Block(previous_hash)
        
        return self.current_block
    
    # Adds an incoming transaction to a list of pending transactions
    def add_transaction_to_pending(self, transaction: Transaction):
        # Add transaction to pending list
        self.pending_transactions.appendleft(transaction)
        return
    
    # Updates the balance for each node given a validated transaction
    def update_wallet_state(self, transaction: Transaction):
        print("========= NEW TRANSACTION 💵 ===========")
        # 1. If the transaction is related to node, update wallet
        if (transaction.receiver_address == self.wallet.address or 
            transaction.sender_address == self.wallet.address):
            self.wallet.transactions.append(transaction)
        #debug 
        print(f"Transaction added to blockchain: {self.ring[transaction.sender_address]['id']} -> {self.ring[transaction.receiver_address]['id']} : {transaction.amount} BCCs")
        
        # 2. Update the balance of sender and receiver in the ring.
        self.ring[str(transaction.sender_address)]['balance'] -=  transaction.amount
        self.ring[str(transaction.receiver_address)]['balance'] +=  transaction.amount
        # debug
        # print("2. Updated ring: ", self.ring.values())
        return


    def update_original_utxos(self, transaction: Transaction):
        # UTXO attributes
        sender_address = transaction.sender_address
        receiver_address = transaction.receiver_address
        amount = transaction.amount
        sender_id = self.ring[str(sender_address)]['id']
        receiver_id = self.ring[str(receiver_address)]['id']
        
        # Update sender UTXOs
        total_amount = 0
        while(total_amount < amount):
            try:
                temp_utxo = self.blockchain.UTXOs[sender_id].popleft()
                total_amount += temp_utxo.amount
            except:
                print("‼️ Not enough UTXOs for : ", sender_id)
                break

        if (total_amount > amount):
            # Update receiver UTXOs
            self.blockchain.UTXOs[receiver_id].append(UTXO(sender_id, receiver_id, amount))
            # sender get change
            self.blockchain.UTXOs[sender_id].append(UTXO(sender_id, sender_id, total_amount-amount))
        return
    

    def update_temp_utxos(self, transaction: Transaction):
        # UTXO attributes
        sender_address = transaction.sender_address
        receiver_address = transaction.receiver_address
        amount = transaction.amount
        sender_id = self.ring[str(sender_address)]['id']
        receiver_id = self.ring[str(receiver_address)]['id']

        # Update receiver UTXOs
        self.temp_utxos[receiver_id].append(UTXO(sender_id, receiver_id, amount))
        
        # Update sender UTXOs
        total_amount = 0
        while(total_amount < amount):
            temp_utxo = self.temp_utxos[sender_id].popleft()
            total_amount += temp_utxo.amount
        if (total_amount > amount):
            self.temp_utxos[sender_id].append(UTXO(sender_id, sender_id, total_amount-amount))

        return