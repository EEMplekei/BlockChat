from fastapi import FastAPI, Request, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from colorama import Fore
import os
import uvicorn
import argparse
import pickle
import time
import threading
import socket
import fcntl
import socket
import struct
try:
	from components.node import Node
	from components.transaction import Transaction, TransactionType
except ImportError:
	print(f"{Fore.RED}Could not import required classes{Fore.RESET}")
	exit()

try:
    load_dotenv()
    block_size = int(os.getenv('BLOCK_SIZE'))
except Exception as e:
    print(f"{Fore.RED}Error loading environment variables: {e}{Fore.RESET}")
    print(f"{Fore.YELLOW}Using default block size: 3{Fore.RESET}")
    block_size = 3

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
		sender_address = '0',
		receiver_address = node.wallet.address, 
		type_of_transaction = TransactionType.COINS,
		payload = total_bbc,
		nonce = 1
	)
 
	# Add transaction to genesis block
	gen_block.transactions.append(first_transaction)
	gen_block.calculate_hash()
	# Add genesis block to blockchain
	node.blockchain.chain.append(gen_block)
	# Create new empty block
	node.current_block = node.create_new_block()
	return

#Parse the arguments and return the IP and port
def get_ip_and_port():
	
	argParser = argparse.ArgumentParser()
	argParser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
	argParser.add_argument("-i", "--interface", help="Interface on which the node is running", default="eth2")
	args = argParser.parse_args()

	try:
		ip = get_ip_linux(args.interface)
	except OSError:
		print(f"{Fore.RED}Could not get the IP address of interface {args.interface}{Fore.RESET}")
		return None, None
	port = args.port

	return ip, port

#Get the IPv4 address of a specific interface
def get_ip_linux(interface: str) -> str:

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	packed_iface = struct.pack('256s', interface.encode('utf_8'))
	packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
	return socket.inet_ntoa(packed_addr)


# ======================== MAIN ===========================

# Get info about the node IP and port
ip_address, port = get_ip_and_port()
if(ip_address == None or port == None):
	exit()

#Initialize FastAPI
app = FastAPI()

# Initialize the new node and set it's IP and port
node = Node()
node.ip , node.port = ip_address, str(port)

# Get info about the cluster, bootstrap node
load_dotenv()
total_nodes = int(os.getenv('TOTAL_NODES'))
total_bbc = total_nodes * 1000

bootstrap_node = {
	'ip': os.getenv('BOOTSTRAP_IP'),
	'port': os.getenv('BOOTSTRAP_PORT')
}

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
	node.advertise_to_boostrap()

# ======================== ROUTES =========================
# Client routes 

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

	if receiver_id > (total_nodes - 1) or receiver_id < 0:
		return JSONResponse('Invalid receiver ID', status_code=status.HTTP_400_BAD_REQUEST)

	# Check the type
	if type_of_transaction == "COINS":
		type_of_transaction = TransactionType.COINS
		payload = int(payload)
	elif type_of_transaction == "MESSAGE":
		type_of_transaction = TransactionType.MESSAGE
	else:
		return JSONResponse('Invalid type of transaction', status_code=status.HTTP_400_BAD_REQUEST)

	# Find public key (address) corresponding to receiver_id
	receiver_address = None
	for key, value in node.ring.items():
		if value['id'] == receiver_id:
			receiver_address = key
	
	if receiver_address != None:
		try:
			# Create transaction function also signs it and validates it inside
			transaction = node.create_transaction(receiver_address, type_of_transaction, payload)
   
   			# Add to pending transactions list and check that it should pass
			if not node.add_transaction_to_pending(transaction):
				return JSONResponse('Transaction is not valid', status_code=status.HTTP_400_BAD_REQUEST)
			
			print("Transaction added to pending list :comment on create transation call")
			# Broadcast transaction			
			node.broadcast_transaction(transaction)
			# Check if block is full
			node.check_if_block_is_full_to_mint()
			
			return JSONResponse('Successful Transaction !', status_code=status.HTTP_200_OK)
		except Exception as e:
			print(f"{Fore.RED}Error create_transaction: {e}{Fore.RESET}")
			return JSONResponse("Could not create transaction", status_code=status.HTTP_400_BAD_REQUEST)
	else:
		return JSONResponse('Receiver not found', status_code=status.HTTP_400_BAD_REQUEST)

@app.post("/api/set_stake")
async def set_stake(request: Request):
	# json body request expected to be:
	# {
	#     "stake": int,
	# }
 
	# Get the parameters
	data = await request.json()
	amount = data.get("stake")
	
	#Input validation
	try:
		amount = int(amount)
	except ValueError:
		return JSONResponse('Stake must be an integer number', status_code=status.HTTP_400_BAD_REQUEST)
	if(amount <= 0):
		return JSONResponse('Stake must be greater than 0', status_code=status.HTTP_400_BAD_REQUEST)

	# Create transaction function also validates it inside
	staking_transaction = node.create_transaction(0, TransactionType.COINS, amount)
	
	# Add to pending transactions list and check that it was added to pending
	if not node.add_transaction_to_pending(staking_transaction):
		return JSONResponse('Transaction is not valid', status_code=status.HTTP_400_BAD_REQUEST)

	# Add to pending transactions list
	node.add_transaction_to_pending(staking_transaction)
    # Broadcast transaction
	node.broadcast_transaction(staking_transaction)
	return JSONResponse('Successful Staking !', status_code=status.HTTP_200_OK)

@app.get("/api/view_last_block")
def view_last_block_transactions():
	
	if (len(node.blockchain.chain) < 1):
		return Response(status_code = status.HTTP_204_NO_CONTENT)
	
	# Get last block in the chain
	latest_block = node.blockchain.chain[-1]
 
	# Return a list of transactions
	try:
		transactions = latest_block.get_transactions_from_block(node)
	except Exception as e:
		print(f"{Fore.RED}Error view_last_block_transactions: {e}{Fore.RESET}")
		return JSONResponse('Could not get transactions from block', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
	return JSONResponse(transactions, status_code=status.HTTP_200_OK)

@app.get("/api/get_balance")
def get_balance():
	try:
		balance = node.ring[str(node.wallet.address)]['balance'] # Alternative
	except Exception as e:
		print(f"{Fore.RED}Error get_balance: {e}{Fore.RESET}")
		return JSONResponse('Could not get balance', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return JSONResponse({'balance': balance}, status_code=status.HTTP_200_OK)

@app.get("/api/get_temp_balance")
def get_temp_balance():
	try:
		temp_balance = node.ring[str(node.wallet.address)]['temp_balance'] # Alternative
	except Exception as e:
		print(f"{Fore.RED}Error get_temp_balance: {e}{Fore.RESET}")
		return JSONResponse('Could not get temp_balance', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)	
	return JSONResponse({'temp_balance': temp_balance}, status_code=status.HTTP_200_OK)

@app.get("/api/get_chain_length")
def get_chain_length():
	return JSONResponse({'chain_length': len(node.blockchain.chain)}, status_code=status.HTTP_200_OK)

@app.get("/api/get_chain")
def get_chain():
	return Response(pickle.dumps(node.blockchain), status_code=status.HTTP_200_OK)

# =========================================================
# Internal routes

@app.get("/")
async def root():
	return {"message": f"Welcome to BlockChat"}

@app.post("/receive_ring")
# Gets the completed list of nodes from Bootstrap node after all nodes have joined
async def receive_ring(request: Request):
	
	if (node.is_bootstrap):
		return JSONResponse('Cannot post ring to bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)
	
	data = await request.body()
	node.ring = pickle.loads(data)

	print("Ring received successfully !")
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

	# Check if block is full
	node.check_if_block_is_full_to_mint()

	return JSONResponse('OK')

@app.post("/get_block")
def get_block(data: bytes = Depends(get_body)):
	# Gets an incoming mined block and adds it to the blockchain.
	
	# data = request.body()
	new_block = pickle.loads(data)

	print(f"{Fore.GREEN}NEWS{Fore.RESET}: Got new block, now lets validate it !")

	# Wait until incoming block has finished processing
	with (node.processing_block_lock):
		#print("Processing block: ", node.processing_block)
		# Check validity of block		
		if (new_block.validate_block(node.blockchain.chain[-1].hash, node.current_validator)):
			print("Incoming block is valid")
			# If it is valid:
			# Stop the current block mining
			with(node.incoming_block_lock):
				#print("Incoming block: ", node.incoming_block)
				node.incoming_block = True
			# node.processing_block = False
			print("Block was ⛏️  by someone else 🧑")
			# Add block to the blockchain
			print("✅📦! Adding it to the chain")
			node.add_block_to_chain(new_block)
			print("Blockchain length: ", len(node.blockchain.chain))
			return JSONResponse('OK')
		# Check if latest_block.previous_hash == incoming_block.previous_hash
		# elif(node.blockchain.chain[-1].previous_hash == new_block.previous_hash):
		# 	print("🗑️  Rejected incoming block")
		# else:
		# 	print("Incoming block previous_hash: ", new_block.previous_hash)
		# 	print("🔗 BLOCKCHAIN 🔗")
		# 	print([block.hash[:7] for block in node.blockchain.chain])
		# 	# Resolve conflict in case of wrong previous_hash
		# 	node.blockchain.resolve_conflict(node)
		print("❌📦 Something went wrong with validation 🙁")

		return JSONResponse('Error validating block', status_code=status.HTTP_400_BAD_REQUEST)

@app.post("/let_me_in")
async def let_me_in(request: Request):
	# ! BOOTSTRAP ONLY !
	# Adds a new node to the cluster
	if node.is_bootstrap:
		# Deserialize the data received in the request body using pickle.loads()
		data = await request.body()
		node_data = pickle.loads(data)

		# Extract necessary parameters from the deserialized data
		ip = node_data.get('ip')
		port = node_data.get('port')
		address = node_data.get('address')
		id = len(node.ring)

		# Add node to the ring
		node.add_node_to_ring(id, ip, port, address,0)

		# Check if all nodes have joined 
		# !! (do it after you have responded to the last node)
		t = threading.Thread(target=check_full_ring)
		t.start()

		return JSONResponse({'id': id})
	else:
		return JSONResponse('Cannot post to let-me-in to a non-bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)

def check_full_ring():
	# ! BOOTSTRAP ONLY !
	# Checks if all nodes have been added to the ring
	time.sleep(1)
	if (len(node.ring) == total_nodes):
		node.broadcast_ring()
		node.broadcast_blockchain()
		node.broadcast_initial_bcc()
		

# WEB SERVER RUN
uvicorn.run(app, host=None, port = port)
