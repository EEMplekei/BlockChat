from collections import deque
from copy import deepcopy
from dotenv import load_dotenv
import requests
import pickle
import json
import os
import random
import threading


from wallet import Wallet
from blockchain import Blockchain
from transaction import TransactionType, Transaction
from block import Block


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
        # incoming_block: True if there has been received another mined
        # processing_block: True if there is a new incoming block waiting to get validated (used in api.py)
        # pending_transactions:  List of transactions destined to be mined

        # incoming_block_lock:    Lock for incoming_block variable
        # processing_block_lock:  Lock for processing_block variable
        
        self.wallet = Wallet() # create_wallet
        self.ip = None
        self.port = None
        self.id = None
        self.stake = 0 
        self.ring = {}     # address: {id, ip, port, balance}
        self.blockchain = Blockchain()
        self.is_bootstrap = False
        self.incoming_block = False
        self.processing_block = False
        self.pending_transactions = deque()
        self.incoming_block_lock = threading.Lock()
        self.processing_block_lock = threading.Lock()
        self.nonce = random.randint(0, 10000)

    #Creates a new block for the blockchain
    def create_new_block(self):
        previous_hash = None
        # Special case for GENESIS block
        if (len(self.blockchain.chain) == 0):
            previous_hash = 1
        elif (len(self.blockchain.chain) > 0):
            previous_hash = self.blockchain.chain[-1].hash
            
        self.current_block = Block(previous_hash, self.wallet.address)
        
        return self.current_block
    
    # Adds a transaction to a list of pending transactions
    def add_transaction_to_pending(self, transaction: Transaction):
        # Before we add to pending list we will call validate_transaction to check if the transaction is valid

        # If it is valid we will add it to the pending list
        self.pending_transactions.appendleft(transaction)
        self.update_temp_balance(transaction)
        return
    
    # Send the current state of the blockchain to a specific node via HTTP POST request.
    def update_temp_balance(self, transaction: Transaction):
        if (transaction.receiver_address == 0):
            # IF IT IS STAKE CASE
            self.ring[str(transaction.sender_address)]['stake'] = transaction.amount
            self.ring[str(transaction.sender_address)]['temp_balance'] -= transaction.amount
        elif (transaction.type_of_transaction == TransactionType.MESSAGE):
            # IF IT IS message
            self.ring[str(transaction.sender_address)]['temp_balance'] -= len(transaction.message)
            self.ring[str(transaction.receiver_address)]['temp_balance'] += len(transaction.message)
        else: 
            # IF IT IS NORMAL TRANSACTION COINS
            # Update the temporary balance of the sender and receiver in the ring.
            self.ring[str(transaction.sender_address)]['temp_balance'] -= transaction.amount
            self.ring[str(transaction.receiver_address)]['temp_balance'] += transaction.amount
        return

    # Updates the balance for each node given a validated transaction
    def update_wallet_state(self, transaction: Transaction):
        print("========= NEW TRANSACTION 💵 ===========")
        # If the transaction is related to node, update wallet
        if (transaction.receiver_address == self.wallet.address or 
            transaction.sender_address == self.wallet.address):
            self.wallet.transactions.append(transaction)
        # info message
        print(f"1. Transaction added to blockchain: {self.ring[str(transaction.sender_address)]['id']} -> {self.ring[str(transaction.receiver_address)]['id']} : {transaction.amount} BBCs")
        
        # Update the balance of sender and receiver in the ring.
        self.ring[str(transaction.sender_address)]['balance'] -=  transaction.amount
        self.ring[str(transaction.receiver_address)]['balance'] +=  transaction.amount
        return

    # Update pending transactions list from incoming block
    def update_pending_transactions(self, incoming_block: Block):
        """
        Given a newly block (incoming_block) by validator,
        compare the transaction_list that you hold with incoming_block's transactions.
        Update the pending transactions list so you void executing it a second time
        """
        # Create a set of transaction IDs in incoming_block for faster lookup
        incoming_transactions_ids = {tx.transaction_id for tx in incoming_block.transactions_list}

        # Remove transactions from pending_transactions if their IDs are in incoming_transactions_ids
        self.pending_transactions = [tx for tx in self.pending_transactions if tx.transaction_id not in incoming_transactions_ids]

    def mint_block(self):
        """
        ! VALIDATOR ONLY !
        Given a list of pending transactions, create a new block and broadcast it to the network
        """
        if(len(self.pending_transactions) < block_size):
             print(f"⛔️ Not enough transactions to mint a block. ({len(self.pending_transactions)}/{block_size})")
        # call proof of stake
        # if public key that proof of stake outputs is mine do the following:
        # Create new block
        new_block = self.create_new_block()
        # Add transactions to the new block
        for _ in range(block_size):
            new_block.add_transaction(self.pending_transactions.pop())
            new_block.transactions.append(transaction)
        # Calculate hash
        new_block.calculate_hash()
        # Add block to blockchain
        self.add_block_to_chain(new_block)
        # Broadcast block to the network
        self.broadcast_block(new_block)



    # Adds a newly block to the chain (assuming it has been validated)
    def add_block_to_chain(self, block: Block):
        # Add block to original chain
        self.blockchain.chain.append(block)
        # Update wallet 
        for transaction in block.transactions_list:
            self.update_wallet_state(transaction)
        # Update pending_transactions list
        self.update_pending_transactions(block)
        # Add transactions to blockchain set
        for t in block.transactions_list:
            self.blockchain.transactions_hashes.add(t.transaction_id)
        # debug
        print("🔗 BLOCKCHAIN 🔗")
        print([block.hash[:7] for block in self.blockchain.chain])


    # Unicast a validated block
    def unicast_block(self, node, block):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_block'
        requests.post(request_url, pickle.dumps(block))
    
    # Broadcast a validated block
    def broadcast_block(self, block: Block):
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_block(node, block)

    ### Stake ###     
    def unicast_stake(self, node, stake):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_stake'
        requests.post(request_url, pickle.dumps(stake))

    def broadcast_stake(self, stake):
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_stake(node, stake)
    
    ##### Transaction #####
    def create_transaction(self, receiver_address, type_of_transaction, payload):
        # Assume receiver_address is valid
        sender_address = self.wallet.address
        nonce = self.nonce
        # Create a new transaction
        transaction = Transaction(sender_address, receiver_address, type_of_transaction, payload, nonce)
        # Sign it
        transaction.sign_transaction(self.wallet.private_key)
        # Validate it
        if transaction.validate_transaction(self.ring[str(self.wallet.address)]['temp_balance']) == False:
            return False
        self.nonce += 1
        return transaction
        

    def unicast_transaction(self, node, transaction):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_transaction'
        requests.post(request_url, pickle.dumps(transaction))
        
    def broadcast_transaction(self, transaction):
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_transaction(node, transaction)


    ##### Bootstrap Node #####
    # The following methods are used only by the bootstrap node
    
    # Adds a new node to the cluster
    def add_node_to_ring(self, id, ip, port, address, balance):
        self.ring[str(address)] = {
                'id': id,
                'ip': ip,
                'port': port,
                'stake': 0, # stake is 0 for new nodes
                'balance': balance,
                'temp_balance': balance, # temp_balance to keep track balance while transactions are on pending list
            }
        
        return
    
    # Sends information about self to the bootstrap node
    def unicast_node(self, node):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/let_me_in'
        response = requests.post(request_url, data={
            'ip': self.ip,
            'port': self.port,
            'address': self.wallet.address
        })

        if response.status_code == 200:
            print("Node added successfully !")
            self.id = response.json()['id']
            print('My ID is: ', self.id)
        else:
            print("Initiallization failed")
    
    # Send the current ring information to a specific node via HTTP POST request.
    def unicast_ring(self, node):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/receive_ring'
        requests.post(request_url, pickle.dumps(self.ring))

    # Broadcast the current ring information to all nodes
    def broadcast_ring(self):
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_ring(node)

    # Send the current state of the blockchain to a specific node
    def unicast_blockchain(self, node):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_blockchain'
        requests.post(request_url, pickle.dumps(self.blockchain))

    # Broadcast the current state of the blockchain to all nodes
    def broadcast_blockchain(self):
        """
        ! BOOTSTRAP ONLY !
        Broadcast the current state of the blockchain to all nodes
        """
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_blockchain(node)
    
    # Send the initial amount of 1000 BlockChat coins to a specific node
    def unicast_initial_bcc(self, node_address):
        # Create initial transaction
        transaction = self.create_transaction(node_address,TransactionType.COINS, 1000)

        # Add transaction to pending list
        self.add_transaction_to_pending(transaction)

        # Broadcast transaction to other nodes in the network
        self.broadcast_transaction(transaction)
    
    # Send the initial amount of 1000 BlockChat coins to all nodes
    def broadcast_initial_bcc(self):
        for node_address in self.ring:
            if (self.id != self.ring[str(node_address)]['id']):
                self.unicast_initial_bcc(node_address)
