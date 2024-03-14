from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import JSONResponse
from components.node import node
from helper_functions.env_variables import TOTAL_NODES
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
@internal_api.post("/receive_blockchain")
async def receive_blockchain(request: Request):
	
	if len(node.ring) < TOTAL_NODES:
		return JSONResponse('Ring is not full yet', status_code=status.HTTP_400_BAD_REQUEST)
 
	if (node.is_bootstrap):
		return JSONResponse('Cannot post blockchain to bootstrap node', status_code=status.HTTP_400_BAD_REQUEST)
	
	data = await request.body()
	node.blockchain = pickle.loads(data)

	print("Blockchain received successfully!")
	return JSONResponse('OK')

async def get_body(request: Request):
	return await request.body()

# Gets an incoming transaction and adds it in the block.
@internal_api.post("/receive_transaction")
def receive_transaction(data: bytes = Depends(get_body)):
    if len(node.ring) < TOTAL_NODES:
        return JSONResponse('Ring is not full yet', status_code=status.HTTP_400_BAD_REQUEST)

    new_transaction = pickle.loads(data)
    if not node.is_transaction_replayed(new_transaction):
        if node.add_transaction_to_pending(new_transaction):
            print("New transaction received successfully!")
            return JSONResponse('OK')
        else:
            print("Transaction could not be added to pending transactions. Maybe the sender does not have enough BCCs")
            return JSONResponse('Error adding transaction. Not enough coins!', status_code=status.HTTP_400_BAD_REQUEST)
    else:
        print("Transaction is already seen. Ignoring it.")
        return JSONResponse('Error adding transaction. Transaction is already seen!', status_code=status.HTTP_400_BAD_REQUEST)


# Gets an incoming mined block and adds it to the blockchain.
@internal_api.post("/receive_block")
def receive_block(data: bytes = Depends(get_body)):
	
	if len(node.ring) < TOTAL_NODES:
		return JSONResponse('Ring is not full yet', status_code=status.HTTP_400_BAD_REQUEST)
	
	# Deserialize the data received in the request body using pickle.loads()
	new_block = pickle.loads(data)

	print(f"{Fore.GREEN}NEWS{Fore.RESET}: Got new block, now lets validate it!")

	# Wait until incoming block has finished processing
	with (node.processing_block_lock):
		# Check validity of block		
		if (new_block.validate_block(node.blockchain.chain[-1].hash, node.current_validator[node.block_counter])):
			node.block_counter += 1
			print(f"{Fore.LIGHTGREEN_EX}Block was mined by someone else\n✅📦 Adding it to the chain{Fore.RESET}")
			# Add block to the blockchain
			node.add_block_to_chain(new_block)
			return JSONResponse('OK')
		print("❌📦 Something went wrong with validation 🙁")

		return JSONResponse('Error validating block', status_code=status.HTTP_400_BAD_REQUEST)

# Gets the order to find validator from the Bootstrap node
@internal_api.post("/find_validator")
async def find_validator():
	if len(node.ring) < TOTAL_NODES:
		return JSONResponse('Ring is not full yet', status_code=status.HTTP_400_BAD_REQUEST)

	node.find_next_validator()
	return {"message": "Validator search initiated"}

# Asks bootstrap node to enter the network, api endpoint accessed by non-bootstrap nodes
@internal_api.post("/join_request")
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