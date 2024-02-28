from fastapi import FastAPI, Request, Depends, APIRouter, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from copy import deepcopy
import os
import socket
import json
import uvicorn
import argparse
import pickle
import time
import threading
import requests

from node import Node
from transaction import Transaction, TransactionType
from blockchain import Blockchain

app = FastAPI()

# CORS (Cross-Origin Resource Sharing)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ARGUMENTS
argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
argParser.add_argument("--ip", help="IP of the host")
args = argParser.parse_args()

# Call once function to ensure that genesis block is only created once
def call_once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.called:
            wrapper.called = True
            return func(*args, **kwargs)
        else:
            raise RuntimeError("Function can only be called once.")
    
    wrapper.called = False
    return wrapper

# Function that creates genesis block
@call_once
def create_genesis_block():
    # BOOTSTRAP: Create the first block of the blockchain (GENESIS BLOCK)
    gen_block = node.create_new_block() # previous_hash autogenerates
    # Create first transaction
    first_transaction = Transaction(
        sender_address='0',
        receiver_address=node.wallet.address, 
        type_of_transaction=TransactionType.COINS,
        payload=total_bbc,
        nonce=1
    )
    # Add transaction to genesis block
    gen_block.transactions.append(first_transaction)
    gen_block.calculate_hash() # void
    # Add genesis block to blockchain
    node.blockchain.chain.append(gen_block)
    # Create new empty block
    node.current_block = node.create_new_block()
    return

# ======================== MAIN ========================
# INITIALIZATION
# Initialize the new node
node = Node()

# Get info about the cluster, bootstrap node
load_dotenv()
total_nodes = int(os.getenv('TOTAL_NODES'))
total_bbc = total_nodes * 1000
bootstrap_node = {
    'ip': os.getenv('BOOTSTRAP_IP'),
    'port': os.getenv('BOOTSTRAP_PORT')
}
ip_address = args.ip
port = args.port

# Set node's IP and port
node.ip = ip_address
node.port = str(port)

# See if node is Bootstrap node
if (ip_address == bootstrap_node["ip"] and str(port) == bootstrap_node["port"]):
    node.is_bootstrap = True
    print("I am bootstrap")

# Register node to the cluster as bootstrap node
if (node.is_bootstrap):
    # Add himself to ring
    node.id = 0
    node.add_node_to_ring(node.id, node.ip, node.port, node.wallet.address, total_bbc)
    create_genesis_block()

else:
    node.unicast_node(bootstrap_node)


# ======================== ROUTES ========================
# ========================================================
# CLIENT ROUTES 
@app.post("/api/create_transaction")
async def create_transaction(request: Request):
    # json body request expected to be:
    # {
    #     "receiver_id": int,
    #     "payload": str,
    #     "type_of_transaction": str
    # }

    # Get the parameters
    data = await request.json()
    receiver_id = data.get("receiver_id")
    payload = data.get("payload")
    type_of_transaction = data.get("type_of_transaction")

    if type_of_transaction == "COINS":
        type_of_transaction = TransactionType.COINS
        payload = int(payload)
    elif type_of_transaction == "MESSAGE":
        type_of_transaction = TransactionType.MESSAGE
    
    # Create transaction

    # find pk of receiver
    receiver_address = None
    for node_id, node_info in node.ring.items():
        if node_info['id'] == receiver_id:
            receiver_address = node_info['address']

    transaction = node.create_transaction(receiver_address, type_of_transaction, payload)
    # Add to pending transactions list
    node.add_transaction_to_pending(transaction)
    # Broadcast transaction
    node.broadcast_transaction(transaction)
    return JSONResponse('Successful Transaction !', status_code=status.HTTP_200_OK)


@app.post("/api/set_stake")
async def set_stake(request: Request):
    # json body request expected to be:
    # {
    #     "stake": int,
    # }

    # Get the parameters
    data = await request.json()
    amount = data.get("stake")
    amount = int(amount)

    # Check if amount is negative
    if (amount < 0):
        return JSONResponse(content={"message":'Stake amount cannot be negative'}, status_code=status.HTTP_400_BAD_REQUEST)
    
    # Check if amount is greater than total balance
    if (amount > node.ring[str(node.wallet.address)]['balance']):
        return JSONResponse(content={"message":'Stake amount cannot be greater than total balance'}, status_code=status.HTTP_400_BAD_REQUEST)
    
    # Check if amount is greater than the remaining from pending transactions
    if (amount > node.ring[str(node.wallet.address)]['balance'] - node.get_pending_transactions_amount()):
        return JSONResponse(content={"message":'Stake amount cannot be greater than the remaining from pending transactions'}, status_code=status.HTTP_400_BAD_REQUEST)
    
    # Set stake
    node.ring.stake = amount
    node.stake = amount
    # Broadcast staking
    node.broadcast_stake()
    return JSONResponse('Successful Staking !', status_code=status.HTTP_200_OK)

@app.get("/api/view_last_block")
def view_transactions():
    # Returns the transactions of the last validated, mined block
    if (len(node.blockchain.chain) <= 1):
        return JSONResponse('There are no mined blocks at the moment !')
    
    # Get last block in the chain
    latest_block = node.blockchain.chain[-1]
    # Return a list of transactions (sender, receiver, amount)
    transactions = []
    for transaction in latest_block.transactions_list:
        transactions.append(
            {
                "sender_id": node.ring[transaction.sender_address]['id'],
                # "sender_address": transaction.sender_address,
                "receiver_id": node.ring[transaction.receiver_address]['id'],
                # "receiver_address": transaction.receiver_address,
                "amount": transaction.amount
            }
        )
    return JSONResponse(transactions, status_code=status.HTTP_200_OK)

@app.get("/api/get_balance")
def get_balance():
    # Gets the total balance for the given node (in NBCs)
    # Get the BBCs attribute from the node object
    balance = node.ring[str(node.wallet.address)]['balance'] # Alternative

    return JSONResponse({'balance': balance}, status_code=status.HTTP_200_OK)

@app.get("/api/get_chain_length")
def get_chain_length():
    # Gets the current valid blockchain length of the receiver
    # Get the current length of the node's blockchain
    chain_len = len(node.blockchain.chain)

    return JSONResponse({'chain_length': chain_len}, status_code=status.HTTP_200_OK)

@app.get("/api/get_chain")
def get_chain():
    # Gets the current valid blockchain of the receiver
    # Get the current length of the node's blockchain
    return Response(pickle.dumps(node.blockchain), status_code=status.HTTP_200_OK)



# =================================================
# INTERNAL ROUTES
@app.get("/")
async def root():
    return {"message": f"Welcome to BlockChat"}

@app.post("/get_ring")
async def get_ring(request: Request):
    # Gets the completed list of nodes from Bootstrap node
    data = await request.body()
    node.ring = pickle.loads(data)

    print("Ring received successfully !")
    return JSONResponse('OK')

@app.post("/get_stake")
async def get_stake(request: Request):
    # Gets the stake of the nodes from Bootstrap node
    data = await request.body()
    node.stake = pickle.loads(data)

    print("Stake received successfully !")
    return JSONResponse('OK')

@app.post("/get_blockchain")
async def get_blockchain(request: Request):
    # Gets the lastest version of the blockchain from the Bootstrap node
    data = await request.body()
    node.blockchain = pickle.loads(data)

    print("Blockchain received successfully !")
    return JSONResponse('OK')

async def get_body(request: Request):
    return await request.body()

@app.post("/get_transaction")
def get_transaction(data: bytes = Depends(get_body)):
    # Gets an incoming transaction and adds it in the block.

    # data = request.body()
    new_transaction = pickle.loads(data)
    print("New transaction received successfully !")

    # Add transaction to block
    node.add_transaction_to_pending(new_transaction)

    return JSONResponse('OK')

@app.post("/get_block")
def get_block(data: bytes = Depends(get_body)):
    # Gets an incoming mined block and adds it to the blockchain.
    
    # data = request.body()
    new_block = pickle.loads(data)
    print("New block received successfully !")

    # Wait until incoming block has finished processing
    with (node.processing_block_lock):
        # Check validity of block
        if (new_block.validate_block(node.blockchain)):
            # If it is valid:
            # Stop the current block mining
            with(node.incoming_block_lock):
                node.incoming_block = True
            # node.processing_block = False
            print("Block was ⛏️  by someone else 🧑")
            # Add block to the blockchain
            print("✅📦! Adding it to the chain")
            node.add_block_to_chain(new_block)
            print("Blockchain length: ", len(node.blockchain.chain))
        
        # Check if latest_block.previous_hash == incoming_block.previous_hash
        elif(node.blockchain.chain[-1].previous_hash == new_block.previous_hash):
            print("🗑️  Rejected incoming block")
        else:
            print("Incoming block previous_hash: ", new_block.previous_hash)
            print("🔗 BLOCKCHAIN 🔗")
            print([block.hash[:7] for block in node.blockchain.chain])
            # Resolve conflict in case of wrong previous_hash
            node.blockchain.resolve_conflict(node)
            print("❌📦 Something went wrong with validation 🙁")

        return JSONResponse('OK')

@app.post("/let_me_in")
async def let_me_in(request: Request):
    # ! BOOTSTRAP ONLY !
    # Adds a new node to the cluster
    
    # Get the parameters
    data = await request.form()
    ip = data.get('ip')
    port = data.get('port')
    address = data.get('address')
    id = len(node.ring)

    # Add node to the ring
    node.add_node_to_ring(id, ip, port, address,0)

    # Check if all nodes have joined 
    # !! (do it after you have responded to the last node)
    t = threading.Thread(target=check_full_ring)
    t.start()

    return JSONResponse({'id': id})

def check_full_ring():
    # ! BOOTSTRAP ONLY !
    # Checks if all nodes have been added to the ring
    time.sleep(1)
    if (len(node.ring) == total_nodes):
        node.broadcast_ring()
        node.broadcast_blockchain()
        node.broadcast_initial_bcc()
        

# WEB SERVER RUN    
uvicorn.run(app, host="0.0.0.0", port=port)
