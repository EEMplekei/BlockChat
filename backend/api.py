from fastapi import FastAPI, Request, Depends, status, Response
from fastapi.responses import JSONResponse
from colorama import Fore
from dotenv import load_dotenv
import uvicorn
import pickle
import threading

try:
	from helper_functions.env_variables import *
	from components.node import Node
	from components.transaction import TransactionType
except ImportError:
	print(f"{Fore.RED}Could not import required classes{Fore.RESET}")
	exit()

# ======================== MAIN ===========================

# Initialize environment variables
load_dotenv()
TOTAL_NODES = int(try_load_env('TOTAL_NODES'))
FEE_RATE = float(try_load_env('FEE_RATE'))

#Initialize FastAPI
app = FastAPI()

# Initialize the new node and set it's IP and port (happens in the constructor)
# The node will be a bootstrap node if it's ip and port match the bootstrap node's ip and port
node = Node()
node.register_node_to_cluster()

# ======================== ROUTES =========================
# Client routes 
@app.get("/")
async def root():
	return JSONResponse({"message": f"Welcome to BlockChat. Node: {node.id}"}, status_code=status.HTTP_200_OK)

@app.post("/api/create_transaction")
async def create_transaction(request: Request):
	# json body request expected to be:
	# {
	#     "receiver_id": int,
	#     "payload": str,
	#     "type_of_transaction": str
	# }
	
	# It shouldnt be here, but just in case
	if node.current_validator is None:
		node.find_next_validator()

	# Get the parameters
	data = await request.json()
	receiver_id = data.get("receiver_id")
	payload = data.get("payload")
	type_of_transaction = data.get("type_of_transaction")

	if receiver_id > (TOTAL_NODES - 1) or receiver_id < 0:
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

	# Get the validator address
	validator_address = node.current_validator
	print(f"Validator address: {validator_address[1]} 🧑")
	if receiver_address != None:
		try:
			# Create transaction function also signs it and validates it inside
			transaction = node.create_transaction(receiver_address, type_of_transaction, payload)

			# Create transaction fee
			if type_of_transaction == TransactionType.COINS:
				transaction_fee = node.create_transaction(validator_address, TransactionType.FEE, payload*FEE_RATE)
			elif (type_of_transaction == TransactionType.MESSAGE):
				transaction_fee = node.create_transaction(validator_address, TransactionType.FEE, len(payload)*FEE_RATE)

   			# Add to pending transactions list and check that it should pass
			if not node.add_transaction_to_pending(transaction):
				return JSONResponse('Transaction is not valid', status_code=status.HTTP_400_BAD_REQUEST)
			# Broadcast transaction			
			node.broadcast_transaction(transaction)

			# Add to pending transactions list and check that it should pass
			if not node.add_transaction_to_pending(transaction_fee):
				return JSONResponse('Transaction is not valid', status_code=status.HTTP_400_BAD_REQUEST)
			# Broadcast transaction			
			node.broadcast_transaction(transaction_fee)
			
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
		return JSONResponse('Staking is not valid', status_code=status.HTTP_400_BAD_REQUEST)

	# Broadcast transaction
	node.broadcast_transaction(staking_transaction)
	return JSONResponse('Successful Staking!', status_code=status.HTTP_200_OK)

@app.get("/api/view_last_block")
def view_last_block_transactions():
	
	if (len(node.blockchain.chain) < 1):
		return Response(status_code = status.HTTP_204_NO_CONTENT)
	# Get last block in the chain
	latest_block = node.blockchain.chain[-1]
	data = []
	# Return a list of transactions
	try:
		data.append({
			"hash": str(latest_block.hash)[:7],
			"previous_hash": str(latest_block.previous_hash)[:7],
			"validator": str(node.ring[str(latest_block.validator)]['id']),
			"transactions": latest_block.get_transactions_from_block(node),
		})
	except Exception as e:
		print(f"{Fore.YELLOW}view_last_block_transactions{Fore.RESET}: {Fore.RED}Error: {e}{Fore.RESET}")
		return JSONResponse('Could not get transactions from block', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
	return JSONResponse(data, status_code=status.HTTP_200_OK)

@app.get("/api/get_balance")
def get_balance():
	try:
		balance = node.ring[str(node.wallet.address)]['balance'] # Alternative
	except Exception as e:
		print(f"{Fore.RED}Error get_balance: {e}{Fore.RESET}")
		return JSONResponse('Could not get balance', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return JSONResponse({'balance': balance}, status_code=status.HTTP_200_OK)

@app.get("/api")
def get_api():
	return JSONResponse({'message': 'API UP AND READY!'}, status_code=status.HTTP_200_OK)

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

@app.get("/api/get_pending_list_length")
def get_pending_list_length():
	return JSONResponse({'pending_list_length': len(node.pending_transactions)}, status_code=status.HTTP_200_OK)

@app.get("/api/get_chain")
def get_chain():
	data = []
	# Iterate through the blockchain and get the transactions, hash and previous hash and get the validator of each block
	for block in node.blockchain.chain:
		data.append({
			"hash": str(block.hash)[:7],
			"previous_hash": str(block.previous_hash)[:7],
			"validator": str(node.ring[str(block.validator)]['id']),
			"transactions": block.get_transactions_from_block(node),
		})
	return JSONResponse(data, status_code=status.HTTP_200_OK)

# =========================================================
# Internal routes

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
	# Gets the latest version of the blockchain from the Bootstrap node
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
	
	# Deserialize the data received in the request body using pickle.loads()
	new_block = pickle.loads(data)

	print(f"{Fore.GREEN}NEWS{Fore.RESET}: Got new block, now lets validate it !")

	# Wait until incoming block has finished processing
	with (node.processing_block_lock):
		# Check validity of block		
		if (new_block.validate_block(node.blockchain.chain[-1].hash, node.current_validator)):
			print("Incoming block is valid")
			print("Block was ⛏️  by someone else 🧑")
			# Add block to the blockchain
			print("✅📦! Adding it to the chain")
			node.add_block_to_chain(new_block)
			return JSONResponse('OK')
		print("❌📦 Something went wrong with validation 🙁")

		return JSONResponse('Error validating block', status_code=status.HTTP_400_BAD_REQUEST)

@app.post("/let_me_in")
async def let_me_in(request: Request):
	# ! BOOTSTRAP ONLY !
	# Adds a new node to the cluster
	if not node.is_bootstrap:
		return JSONResponse('Cannot post to let-me-in to a non-bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)

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
	t = threading.Thread(target=node.check_full_ring, args=(len(node.ring), ))
	t.start()

	return JSONResponse({'id': id})

# WEB SERVER RUN
uvicorn.run(app, host = None, port = int(node.port))
