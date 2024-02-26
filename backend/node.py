# NODE 

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
        # incoming_block: True if there has been received another mined
        # processing_block: True if there is a new incoming block waiting to get validated (used in api.py)
        # pending_transactions:  List of transactions destined to be mined

        # incoming_block_lock:    Lock for incoming_block variable
        # processing_block_lock:  Lock for processing_block variable
        
        self.wallet = Wallet() # create_wallet
        self.ip = None
        self.port = None
        self.id = None
        self.ring = {}     # address: {id, ip, port, balance}
        self.blockchain = Blockchain()
        self.is_bootstrap = False
        self.incoming_block = False
        self.processing_block = False
        self.pending_transactions = deque()
        self.incoming_block_lock = threading.Lock()
        self.processing_block_lock = threading.Lock()
        self.stake = None
        self.nonce = random.randint(0, 10000)

    #Creates a new block for the blockchain
    def create_new_block(self):
        previous_hash = None
        # Special case for GENESIS block
        if (len(self.blockchain.chain) == 0):
            previous_hash = 1
            
        self.current_block = Block(previous_hash)
        
        return self.current_block
    
    # Adds a transaction to a list of pending transactions
    def add_transaction_to_pending(self, transaction: Transaction):
        self.pending_transactions.appendleft(transaction)
        return
    
    # Updates the balance for each node given a validated transaction
    def update_wallet_state(self, transaction: Transaction):
        print("========= NEW TRANSACTION 💵 ===========")
        # If the transaction is related to node, update wallet
        if (transaction.receiver_address == self.wallet.address or 
            transaction.sender_address == self.wallet.address):
            self.wallet.transactions.append(transaction)
        # info message
        print(f"1. Transaction added to blockchain: {self.ring[transaction.sender_address]['id']} -> {self.ring[transaction.receiver_address]['id']} : {transaction.amount} NBCs")
        
        # Update the balance of sender and receiver in the ring.
        self.ring[str(transaction.sender_address)]['balance'] -=  transaction.amount
        self.ring[str(transaction.receiver_address)]['balance'] +=  transaction.amount
        return


    def update_utxos(self, transaction: Transaction):
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
    
    # Update pending transactions list from incoming block
    def update_pending_transactions(self, incoming_block: Block):
        """
        Given a newly block (incoming_block) by validator,
        compare the transaction_list that you hold with incoming_block's transactions.
        Update the pending transactions list so you void executing it a second time
        """
        # Remove from pending_transactions all transactions included in the incoming_block
        # for incoming_transaction in incoming_block.transactions_list:
        #     index = 0
        #     while index < len(self.pending_transactions):
        #         pending_transaction = self.pending_transactions[index]
        #         if (pending_transaction.transaction_id == incoming_transaction.transaction_id):
        #             self.pending_transactions.remove(pending_transaction)
        #         else:
        #             index += 1
        # return
        # A more efficient way to do it!!!
        # Create a set of transaction IDs in incoming_block for faster lookup
        incoming_transactions_ids = {tx.transaction_id for tx in incoming_block.transactions_list}

        # Remove transactions from pending_transactions if their IDs are in incoming_transactions_ids
        self.pending_transactions = [tx for tx in self.pending_transactions if tx.transaction_id not in incoming_transactions_ids]

    # Adds a newly block to the chain (assuming it has been validated)
    def add_block_to_chain(self, block: Block):
        # Add block to original chain
        self.blockchain.chain.append(block)
        # Update UTXOs and wallet accordingly
        for transaction in block.transactions_list:
            self.update_utxos(transaction)
            self.update_wallet_state(transaction)
        # Update pending_transactions list
        self.update_pending_transactions(block)
        # Add transactions to blockchain set
        for t in block.transactions_list:
            self.blockchain.trxns.add(t.transaction_id)
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


    ##### Transaction #####
    def create_transaction(self, receiver_address, type_of_transaction, payload):
        sender_address = self.wallet.address
        nonce = self.nonce
        # Create a new transaction
        transaction = Transaction(sender_address, receiver_address, type_of_transaction, payload, type_of_transaction, payload, nonce)
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
                'balance': balance
            }
        
        # Create UTXOs for new node
        self.blockchain.UTXOs.append(deque())

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
        request_url = request_address + '/get_ring'
        requests.post(request_url, pickle.dumps(self.ring))

    # Broadcast the current ring information to all nodes
    def broadcast_ring(self):
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_ring(node)

    # Send the current state of the blockchain to a specific node via HTTP POST request.
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
        # Create a copy of original UTXOs
        self.temp_utxos = deepcopy(self.blockchain.UTXOs)

        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_blockchain(node)
    
    # Send the initial amount of 1000 BlockChat coins to a specific node
    def unicast_initial_bcc(self, node_address):
        # Create initial transaction
        transaction = self.create_transaction(node_address, 1000)

        # Add transaction to pending list
        self.add_transaction_to_pending(transaction)

        # Broadcast transaction to other nodes in the network
        self.broadcast_transaction(transaction)
    
    # Send the initial amount of 1000 BlockChat coins to all nodes
    def broadcast_initial_bcc(self):
        for node_address in self.ring:
            if (self.id != self.ring[node_address]['id']):
                self.unicast_initial_bcc(node_address)

