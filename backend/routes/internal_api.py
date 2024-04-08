from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import JSONResponse
from components.node import node
from utils.env_variables import TOTAL_NODES
from utils.wrappers import check_ring_full
from colorama import Fore
import threading
import pickle

#Initialize FastAPI and add internal network access middleware
internal_api = FastAPI()

@internal_api.get("/", tags=["Internal Routes"])
def root():
	return JSONResponse({"message": f"Welcome to BlockChat. Node: {node.id}"}, status_code=status.HTTP_200_OK)

# Gets the completed list of nodes from Bootstrap node after all nodes have joined
@internal_api.post("/receive_ring", tags=["Internal Routes"])
async def receive_ring(request: Request):
	
	if (node.is_bootstrap):
		return JSONResponse('Cannot post ring to bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)
	
	data = await request.body()
	node.ring = pickle.loads(data)

	return JSONResponse('OK')

# Gets the latest version of the blockchain from the Bootstrap node
@internal_api.post("/receive_blockchain", tags=["Internal Routes"])
@check_ring_full(node)
async def receive_blockchain(request: Request):
	
	if (node.is_bootstrap):
		return JSONResponse('Cannot post blockchain to bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)
	
	data = await request.body()
	node.blockchain = pickle.loads(data)

	print("Blockchain received successfully!")
	return JSONResponse('OK')


# Gets an incoming transaction and adds it in the block.
@internal_api.post("/receive_transaction", tags=["Internal Routes"])
@check_ring_full(node)
async def receive_transaction(request: Request):
	
	data = await request.body()
	new_transaction = pickle.loads(data)

	def add_transaction_thread():
		if not node.is_transaction_replayed(new_transaction):
			if node.add_transaction_to_pending(new_transaction):
				print("New transaction received successfully!")
				return 'OK'
			else:
				print("Transaction could not be added to pending transactions. Maybe the sender does not have enough BCCs")
				return 'Error adding transaction. Not enough coins!'
		else:
			print("Transaction is already seen. Ignoring it.")
			return 'Error adding transaction. Transaction is already seen!'

	thread = threading.Thread(target=add_transaction_thread)
	thread.start()

	return JSONResponse('Processing transaction in the background.', status_code=status.HTTP_202_ACCEPTED)


# Gets an incoming mined block and adds it to the blockchain.
@internal_api.post("/receive_block", tags=["Internal Routes"])
@check_ring_full(node)
async def receive_block(request: Request):
	
	# Deserialize the data received in the request body using pickle.loads()
	data = await request.body()
	new_block = pickle.loads(data)

	print(f"{Fore.LIGHTGREEN_EX}NEWS{Fore.RESET}: Got new block, now lets validate it!")

	# Wait until incoming block has finished processing
	await node.incoming_block_lock.acquire()
	# Check validity of block		
	if (new_block.validate_block(node.blockchain.chain[-1].hash, node.current_validator[len(node.blockchain.chain)+1])):
		print(f"{Fore.LIGHTGREEN_EX}Block was mined by someone else\n✅📦 Adding it to the chain{Fore.RESET}")
		# Add block to the blockchain
		node.add_block_to_chain(new_block)
		return JSONResponse('OK')

	print("❌📦 Something went wrong with validation 🙁")

	return JSONResponse('Error validating block', status_code=status.HTTP_400_BAD_REQUEST)


# Gets the order to find validator from the Bootstrap node
@internal_api.post("/find_validator", tags=["Internal Routes"])
@check_ring_full(node)
async def find_validator():

	node.find_next_validator()
	node.schedule_mint_block(interval=0.1)
	return {"message": "Validator search initiated"}

# Gets the order to release the incoming_block_lock
@internal_api.post("/release_lock", tags=["Internal Routes"])
async def release_lock():
	if node.incoming_block_lock.locked():
		node.incoming_block_lock.release()
		print(f"{Fore.YELLOW}release_lock{Fore.RESET}: {Fore.LIGHTGREEN_EX}Lock released{Fore.RESET}")
	else:
		print(f"{Fore.YELLOW}release_lock{Fore.RESET}: {Fore.LIGHTGREEN_EX}Lock has already been released{Fore.RESET}")
	return {"message": "Lock released"}

# Asks bootstrap node to enter the network, api endpoint accessed by non-bootstrap nodes
@internal_api.post("/join_request", tags=["Internal Routes"])
async def join_request(request: Request):
	
	if not node.is_bootstrap:
		return JSONResponse('Cannot post to join_request to a non-bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)

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