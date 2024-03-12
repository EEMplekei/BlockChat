from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import JSONResponse
from controllers.shared_recourses import node, TOTAL_NODES, FEE_RATE
from backend.helper_functions.middleware import restrict_internal_routes, add_process_time_header
from colorama import Fore
import threading
import pickle

#Initialize FastAPI and add internal network access middleware
internal_api = FastAPI()

@internal_api.get("/")
async def root():
	return JSONResponse({"message": f"Welcome to BlockChat. Node: {node.id}"}, status_code=status.HTTP_200_OK)

# Gets the completed list of nodes from Bootstrap node after all nodes have joined
@internal_api.post("/receive_ring")
async def receive_ring(request: Request):
	
	if (node.is_bootstrap):
		return JSONResponse('Cannot post ring to bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)
	
	data = await request.body()
	node.ring = pickle.loads(data)

	print("Ring received successfully!")
	return JSONResponse('OK')

# Gets the latest version of the blockchain from the Bootstrap node
@internal_api.post("/get_blockchain")
async def get_blockchain(request: Request):

	if (node.is_bootstrap):
		return JSONResponse('Cannot post blockchain to bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)
	
	data = await request.body()
	node.blockchain = pickle.loads(data)

	print("Blockchain received successfully!")
	return JSONResponse('OK')

async def get_body(request: Request):
	return await request.body()

# Gets an incoming transaction and adds it in the block.
@internal_api.post("/get_transaction")
def get_transaction(data: bytes = Depends(get_body)):

	new_transaction = pickle.loads(data)
	print("New transaction received successfully!")

	# Add transaction to block
	node.add_transaction_to_pending(new_transaction)

	return JSONResponse('OK')

# Gets an incoming mined block and adds it to the blockchain.
@internal_api.post("/get_block")
def get_block(data: bytes = Depends(get_body)):
	
	# Deserialize the data received in the request body using pickle.loads()
	new_block = pickle.loads(data)

	print(f"{Fore.GREEN}NEWS{Fore.RESET}: Got new block, now lets validate it!")

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

# Asks bootstrap node to enter the network, api endpoint accessed by non-bootstrap nodes
@internal_api.post("/let_me_in")
async def let_me_in(request: Request):
	
	if not node.is_bootstrap:
		return JSONResponse('Cannot post to let_mein to a non-bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)

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
