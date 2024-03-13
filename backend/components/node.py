from collections import deque
from dotenv import load_dotenv
from colorama import Fore
import requests
import pickle
import os
import random
import threading
import time

#Try loading modules, if it fails, print error and raise ImportError
try:
    from components.wallet import Wallet
    from components.blockchain import Blockchain
    from components.transaction import TransactionType, Transaction
    from components.proof_of_stake import PoSProtocol
    from components.block import Block
    from helper_functions.network import get_ip_and_port
    from helper_functions.env_variables import try_load_env
    from helper_functions.wrappers import call_once, bootstrap_required
except Exception as e:
    print(f"{Fore.YELLOW}node{Fore.RESET}: {Fore.RED}Error loading modules: {e}{Fore.RESET}")
    raise ImportError

# Get environment variables for blocksize, total nodes and bootstrap node
block_size, total_nodes, FEE_RATE = int(try_load_env('BLOCK_SIZE')), int(try_load_env('TOTAL_NODES')), float(try_load_env('FEE_RATE'))
total_bbc = total_nodes * 1000

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
        self.ip, self.port = get_ip_and_port()
        self.id = None
        self.ring = {}     # address: {id, ip, port, balance}
        self.blockchain = Blockchain()
        self.incoming_block = False
        self.processing_block = False
        self.pending_transactions = deque()
        self.current_validator = {}
        self.block_counter = 1
        self.incoming_block_lock = threading.Lock()
        self.processing_block_lock = threading.Lock()
        self.nonce = random.randint(0, 10000)
        self.is_bootstrap = self.check_if_bootstrap()
        
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
        # Validate it here because here we reach and for other's transactions
        
        # FOR STAKE CASE
        if transaction.receiver_address == 0 and transaction.type_of_transaction == TransactionType.COINS:
            old_stake = self.ring[str(transaction.sender_address)]['stake']
            temp_balance = self.ring[str(transaction.sender_address)]['temp_balance']
            if not transaction.validate_transaction(temp_balance + old_stake):
                return False
        else:
            if not transaction.validate_transaction(self.ring[str(transaction.sender_address)]['temp_balance']):
                return False
        
        self.pending_transactions.appendleft(transaction)
        self.update_temp_balance(transaction)
        # Check if the block is full to mint
        self.check_if_block_is_full_to_mint()

        return True
    
    def check_if_block_is_full_to_mint(self):
        if len(self.pending_transactions) >= block_size:
            # Create a thread to mint the block
            mint_thread = threading.Thread(target=self.mint_block)
            mint_thread.start()
        return

    
    # Send the current state of the blockchain to a specific node via HTTP POST request.
    def update_temp_balance(self, transaction: Transaction):
        if (transaction.type_of_transaction == TransactionType.INITIAL): 
            # IF IT IS INITIAL TRANSACTION (DO NOT INCLUDE FEE)
            # Update the temporary balance of the sender and receiver in the ring.
            self.ring[str(transaction.sender_address)]['temp_balance'] -= transaction.amount
            self.ring[str(transaction.receiver_address)]['temp_balance'] += transaction.amount

        elif (transaction.type_of_transaction == TransactionType.COINS and transaction.receiver_address != 0): 
            # IF IT IS NORMAL TRANSACTION COINS
            # Update the temporary balance of the sender and receiver in the ring.
            self.ring[str(transaction.sender_address)]['temp_balance'] -= transaction.amount + transaction.amount*FEE_RATE
            self.ring[str(transaction.receiver_address)]['temp_balance'] += transaction.amount
        
        elif (transaction.type_of_transaction == TransactionType.MESSAGE):
            # IF IT IS message
            self.ring[str(transaction.sender_address)]['temp_balance'] -= len(transaction.message)        
        
        elif (transaction.receiver_address == 0 and transaction.type_of_transaction == TransactionType.COINS):
            # IF IT IS STAKE CASE
            if self.ring[str(transaction.sender_address)]['stake'] != 0:
                # Update Temp Balance
                old_stake = self.ring[str(transaction.sender_address)]['stake']
                self.ring[str(transaction.sender_address)]['temp_balance'] += old_stake

            self.ring[str(transaction.sender_address)]['stake'] = transaction.amount
            self.ring[str(transaction.sender_address)]['temp_balance'] -= transaction.amount
        
        return

    # Updates the balance for each node given a validated transaction
    def update_wallet_state(self, transaction: Transaction):         
        # If the transaction is related to node, update wallet
        if (transaction.receiver_address == self.wallet.address or 
            transaction.sender_address == self.wallet.address):
            self.wallet.transactions.append(transaction)
        # info message
        if(transaction.type_of_transaction == TransactionType.INITIAL):
            print(f"{Fore.LIGHTBLUE_EX}========= INITIAL TRANSACTION 💵 ==========={Fore.RESET}")
            print(f"Transaction added to blockchain: {self.ring[str(transaction.sender_address)]['id']} -> {self.ring[str(transaction.receiver_address)]['id']} : {transaction.amount} BBCs")
            # Update the balance of sender and receiver in the ring.
            self.ring[str(transaction.sender_address)]['balance'] -=  transaction.amount
            self.ring[str(transaction.receiver_address)]['balance'] +=  transaction.amount

        elif(transaction.receiver_address==0 and transaction.type_of_transaction == TransactionType.COINS):
            print(f"{Fore.LIGHTBLUE_EX}============== STAKING 🎰 =============={Fore.RESET}")
            print(f"Transaction added to blockchain: {self.ring[str(transaction.sender_address)]['id']} -> STAKE : {transaction.amount} BBCs")
        
        elif(transaction.type_of_transaction == TransactionType.MESSAGE):
            print(f"{Fore.LIGHTBLUE_EX}=========== NEW MESSAGE 💬 ============={Fore.RESET}")
            print(f"Transaction added to blockchain: {self.ring[str(transaction.sender_address)]['id']} -> {self.ring[str(transaction.receiver_address)]['id']} {str(transaction.message)} : {len(transaction.message)} characters")
            # Update the balance of sender and receiver in the ring.
            self.ring[str(transaction.sender_address)]['balance'] -=  len(transaction.message)
        
        elif(transaction.type_of_transaction == TransactionType.COINS and transaction.receiver_address != 0):
            print(f"{Fore.LIGHTBLUE_EX}========= NEW TRANSACTION 💵 ==========={Fore.RESET}")
            print(f"Transaction added to blockchain: {self.ring[str(transaction.sender_address)]['id']} -> {self.ring[str(transaction.receiver_address)]['id']} : {transaction.amount} BBCs")
            # Update the balance of sender and receiver in the ring.
            self.ring[str(transaction.sender_address)]['balance'] -=  transaction.amount + transaction.amount*FEE_RATE
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
        incoming_transactions_ids = {tx.transaction_id for tx in incoming_block.transactions}

        # Remove transactions from pending_transactions if their IDs are in incoming_transactions_ids
        self.pending_transactions = deque([tx for tx in self.pending_transactions if tx.transaction_id not in incoming_transactions_ids])

    def find_next_validator(self):
        # Create an instance of PoSProtocol
        print("Previous hash: ", self.blockchain.chain[-1].hash)
        protocol = PoSProtocol(self.blockchain.chain[-1].hash)
        # Add nodes to the round
        protocol.add_node_to_round(self.ring)
        # Select a validator
        validator = protocol.select_validator()
        # If the current node is the validator, mint a block
        self.current_validator[self.block_counter] = validator[0]
        # Output what random generator selected
        print(f"🎲 Randomly selected validator for the next Block: {validator[1]}")

    def mint_block(self):
        time.sleep(1)
        with (self.processing_block_lock):
            if len(self.pending_transactions) >= block_size:
                # If the current node is the validator, mint a block
                if self.current_validator[self.block_counter] == str(self.wallet.address):
                    print("🔒 I am the validator")
                    new_block = self.create_new_block()
                    self.block_counter += 1  
                    # Add transactions to the new block
                    for _ in range(block_size):
                        new_block.transactions.append(self.pending_transactions.pop())
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
        sum = 0
        # Update wallet 
        for transaction in block.transactions:
            self.update_wallet_state(transaction)
            # Update the balance of the validator in the ring (if it is a normal COINS transaction)
            if transaction.receiver_address != 0 and transaction.type_of_transaction == TransactionType.COINS:
                self.ring[str(block.validator)]['balance'] += transaction.amount*FEE_RATE
                sum+=transaction.amount*FEE_RATE
                # Make the temp_balance of the receiver equal to the balance 
                self.ring[str(transaction.receiver_address)]['temp_balance'] = self.ring[str(transaction.receiver_address)]['balance']
            # Make the temp_balance of the sender equal to the balance
            self.ring[str(transaction.sender_address)]['temp_balance'] = self.ring[str(transaction.sender_address)]['balance']
        # Make the temp_balance of the validator equal to the balance
        self.ring[str(block.validator)]['temp_balance'] = self.ring[str(block.validator)]['balance']
        # Update pending_transactions list
        self.update_pending_transactions(block)
        # Add transactions to blockchain set
        for t in block.transactions:
            self.blockchain.transactions_hashes.add(t.transaction_id)
        # Output the validator of this block and the total FEES he earned
        print(f"🏆 Block mined by {self.ring[str(block.validator)]['id']} and earned a total of {sum} BBCs as fee")
        print("🔗 BLOCKCHAIN 🔗")
        print([block.hash[:7] for block in self.blockchain.chain])

        print("Blockchain length: ", len(self.blockchain.chain))

        # Select a new validator for the next block
        self.find_next_validator()
        # After you have selected a validator, set the stake of each node in the ring equal to 0
        self.refresh_stake()

    # Refresh the stake of each node
    def refresh_stake(self):
        for node in self.ring.values():
            node['stake'] = 0
        return
    
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
    def create_transaction(self, receiver_address, type_of_transaction: TransactionType, payload):
        # Assume receiver_address is valid
        sender_address = self.wallet.address
        nonce = self.nonce
        # Create a new transaction
        transaction = Transaction(sender_address, receiver_address, type_of_transaction, payload, nonce)
        # Sign it
        transaction.sign_transaction(self.wallet.private_key)
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
    
    # check if transaction already exists in transactions_hashes of blockchain
    def is_transaction_replayed(self, transaction: Transaction):
        # Create a set of transaction IDs in the pending list for faster lookup
        pending_transaction_ids = {tx.transaction_id for tx in self.pending_transactions}
        
        transaction_hash = transaction.transaction_id
        
        # Check if the transaction exists in either blockchain transactions or pending transactions
        if transaction_hash in self.blockchain.transactions_hashes or transaction_hash in pending_transaction_ids:
            return True
        else:
            return False


    def check_if_bootstrap(self):
        if (self.ip, self.port) == (try_load_env('BOOTSTRAP_IP'), str(try_load_env('BOOTSTRAP_PORT'))):
            print(f"I am bootstrap. {Fore.CYAN}My ID is:{Fore.RESET} {Fore.MAGENTA}0 {Fore.RESET}")
            return True
        else:
            return False
        
    def register_node_to_cluster(self):
        if (self.is_bootstrap):
            # Add node to ring
            self.id = 0
            self.add_node_to_ring(self.id, self.ip, self.port, self.wallet.address, total_bbc)
            self.create_genesis_block()
        else:
            self.advertise_to_bootstrap()

    # Sends information about self to the bootstrap node
    def advertise_to_bootstrap(self):
        try:
            bootstrap_address = 'http://' + str(try_load_env('BOOTSTRAP_IP')) + ':' + str(try_load_env('BOOTSTRAP_PORT'))
        except Exception as e:
            print(f"{Fore.RED}Error loading bootstrap ip and port from .env files{Fore.RESET}")
            raise e

        # Data to be sent to the bootstrap node
        data_to_send = {
            'ip': self.ip,
            'port': self.port,
            'address': self.wallet.address
        }
        # Serialize the data using pickle.dumps()
        serialized_data = pickle.dumps(data_to_send)

        # Send the serialized data via POST request
        # Make the call 3 times if cannot connect with delay of 1 second
        for _ in range(3):
            try:
                response = requests.post(bootstrap_address + '/let_me_in', data=serialized_data, timeout = 2)

                if response.status_code == 200:
                    self.id = response.json()['id']
                    print(f"Node added successfully!\n{Fore.CYAN}My ID is:{Fore.RESET} {Fore.MAGENTA}{self.id}{Fore.RESET}")
                    return
                else:
                    print("Initialization failed")
            except requests.exceptions.RequestException as e:
                print(f"{Fore.YELLOW}Can't connect to bootstrap, retrying in 1 second...{Fore.RESET}")
                time.sleep(1)
                continue
        
        print(f"{Fore.RED}Can't connect to bootstrap, please check if the bootstrap node is up and running{Fore.RESET}")
        exit()

    ##### Bootstrap Node #####
    # The following methods are used only by the bootstrap node
    
    # Adds a new node to the cluster
    @bootstrap_required
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
    
    # Send the current ring information to a specific node via HTTP POST request.    
    @bootstrap_required
    def unicast_ring(self, node):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/receive_ring'
        requests.post(request_url, pickle.dumps(self.ring))

    # Broadcast the current ring information to all nodes
    @bootstrap_required
    def broadcast_ring(self):
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_ring(node)

    # Send the current state of the blockchain to a specific node
    @bootstrap_required
    def unicast_blockchain(self, node):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_blockchain'
        requests.post(request_url, pickle.dumps(self.blockchain))

    # Broadcast the current state of the blockchain to all nodes
    @bootstrap_required
    def broadcast_blockchain(self):
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_blockchain(node)
    
    # Send the initial amount of 1000 BlockChat coins to a specific node
    @bootstrap_required
    def unicast_initial_bcc(self, node_address):
        # Create initial transaction
        transaction = self.create_transaction(node_address,TransactionType.INITIAL, 1000)
        
        # Add transaction to pending list
        self.add_transaction_to_pending(transaction)

        # Broadcast transaction to other nodes in the network
        self.broadcast_transaction(transaction)
    
    # Send the initial amount of 1000 BlockChat coins to all nodes
    @bootstrap_required
    def broadcast_initial_bcc(self):
        for node_address in self.ring:
            if (self.id != self.ring[str(node_address)]['id']):
                self.unicast_initial_bcc(node_address)
    
    # Check if all nodes are up
    @bootstrap_required
    def check_all_nodes_are_up(self):
        for node in self.ring.values():
            try:
                response = requests.get(f"http://{node['ip']}:{node['port']}/")
                if response.status_code != 200:
                    return False
            except requests.RequestException as e:
                return False
        return True
    
    # Checks if all nodes have been added to the ring (up until now)
    @bootstrap_required
    def check_full_ring(self, ring_nodes_count): 
        if (ring_nodes_count == total_nodes):
            #Checks that nodes are ready to listen to requests before broadcasting
            while not self.check_all_nodes_are_up():
                #This sleep is here because we want to make sure that all nodes are up before broadcasting
                #We wait so that the API of all nodes are up
                time.sleep(0.5)
            self.broadcast_ring()
            self.broadcast_blockchain()
            self.broadcast_initial_bcc()
            # Select a validator for the first block
            self.find_next_validator()
            # Broadcast the order for the validator
            self.broadcast_order_for_validator()
    
    @bootstrap_required
    def broadcast_order_for_validator(self):
        for node in self.ring.values():
            if (self.id != node['id']):
                request_address = 'http://' + node['ip'] + ':' + node['port']
                request_url = request_address + '/find_validator'
                requests.post(request_url, data=None)
    # Function that creates genesis block
    @call_once
    def create_genesis_block(self):

        # BOOTSTRAP: Create the first block of the blockchain (GENESIS BLOCK)
        gen_block = self.create_new_block() # previous_hash autogenerates
        
        # Create first transaction
        first_transaction = Transaction(
            sender_address = '0',
            receiver_address = self.wallet.address, 
            type_of_transaction = TransactionType.INITIAL,
            payload = total_bbc,
            nonce = 1
        )	
        #Calculate hash of first transaction
        first_transaction.calculate_hash()
        # Add transaction to genesis block
        gen_block.transactions.append(first_transaction)
        gen_block.calculate_hash()
        # Add genesis block to blockchain
        self.blockchain.chain.append(gen_block)
        # Create new empty block
        self.current_block = self.create_new_block()
        return
