from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from components.node import node
from utils.env_variables import TOTAL_NODES
from utils.wrappers import check_ring_full
from components.transaction import TransactionType
from colorama import Fore
import threading
import json
from pydantic import BaseModel

# Define Pydantic model for request body
class Stake(BaseModel):
	stake: int

class CreateTransaction(BaseModel):
	receiver_id: int
	type_of_transaction: str
	payload: str

#Initialize FastAPI fro public routes (all starting with "/api")
public_api = FastAPI(root_path="/api")

# Client routes 
@public_api.get("/", tags=["Public Routes"])
def get_api():
	return JSONResponse({'message': f'Node {node.id} is up and running!'}, status_code=status.HTTP_200_OK)

@public_api.post("/create_transaction", tags=["Public Routes"])
@check_ring_full(node)
async def create_transaction(request: Request, transaction: CreateTransaction):
		
		# Get the parameters
		try:
			data = await request.json()
			receiver_id = data.get("receiver_id")
			payload = data.get("payload")
			type_of_transaction = data.get("type_of_transaction")
		except json.decoder.JSONDecodeError:
			return JSONResponse('Invalid JSON', status_code=status.HTTP_400_BAD_REQUEST)

		if receiver_id > (TOTAL_NODES - 1) or receiver_id < 0:
			return JSONResponse('Invalid receiver ID', status_code=status.HTTP_400_BAD_REQUEST)
		if payload == None:
			return JSONResponse('Payload cannot be empty', status_code=status.HTTP_400_BAD_REQUEST)

		# Check the type
		if type_of_transaction == "COINS":
			type_of_transaction = TransactionType.COINS
			try:
				payload = int(payload)
			except ValueError:
				return JSONResponse('Payload must be an integer number', status_code=status.HTTP_400_BAD_REQUEST)
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
		if receiver_address != None:
			try:
				# Create transaction function also signs it and validates it inside
				transaction = node.create_transaction(receiver_address, type_of_transaction, payload)

				# Add to pending transactions list and check that it should pass
				if not node.add_transaction_to_pending(transaction):
					return JSONResponse('Transaction is not valid', status_code=status.HTTP_400_BAD_REQUEST)
				# Broadcast transaction	
				thread = threading.Thread(target=node.broadcast_transaction, args=(transaction,))
				thread.start()			
				
				return JSONResponse('Successful Transaction!', status_code=status.HTTP_200_OK)
			except Exception as e:
				print(f"{Fore.YELLOW}Error create_transaction: {Fore.RED}{e}{Fore.RESET}")
				return JSONResponse(f"Could not create transaction: {e}", status_code=status.HTTP_400_BAD_REQUEST)
		else:
			return JSONResponse('Receiver not found', status_code=status.HTTP_400_BAD_REQUEST)

@public_api.post("/set_stake", tags=["Public Routes"])
@check_ring_full(node)
async def set_stake(request: Request, stake: Stake):

	# Get the parameters
	data = await request.json()
	amount = data.get("stake")
	
	#Input validation
	try:
		amount = int(amount)
	except ValueError:
		#Shouldn't happen because of the type of the type of Pydantic model
		return JSONResponse('Stake must be an integer number', status_code=status.HTTP_400_BAD_REQUEST)
	if(amount < 0):
		return JSONResponse('Stake must be greater or equal to 0', status_code=status.HTTP_400_BAD_REQUEST)

	# Create transaction function also validates it inside
	staking_transaction = node.create_transaction(0, TransactionType.STAKE, amount)
	
	# Add to pending transactions list and check that it was added to pending
	if not node.add_transaction_to_pending(staking_transaction):
		return JSONResponse('Staking is not valid', status_code=status.HTTP_400_BAD_REQUEST)

	# Broadcast transaction
	node.broadcast_transaction(staking_transaction)
	return JSONResponse('Successful Staking!', status_code=status.HTTP_200_OK)

@public_api.get("/view_last_block", tags=["Public Routes"])
def view_last_block_transactions():	
 
	if (len(node.blockchain.chain) < 1):
		return JSONResponse(status_code = status.HTTP_204_NO_CONTENT)
	# Get last block in the chain
	latest_block = node.blockchain.chain[-1]
	
	# For timestamp
	# Convert the time to a datetime object
	timestamp = datetime.fromtimestamp(latest_block.timestamp)
	# Format the datetime object as a string
	timestamp_string = timestamp.strftime("%Y-%m-%d %H:%M:%S")

	data = []
	# Return a list of transactions
	try:
		data.append({
			"hash": str(latest_block.hash)[:7],
			"previous_hash": str(latest_block.previous_hash)[:7],
			"timestamp": timestamp_string,
			"validator": str(node.ring[str(latest_block.validator)]['id']),
			"total_fees": str(latest_block.get_total_fees()),
			"transactions": latest_block.get_transactions_from_block(node),
		})
	except Exception as e:
		print(f"{Fore.YELLOW}view_last_block_transactions{Fore.RESET}: {Fore.RED}Error: {e}{Fore.RESET}")
		return JSONResponse('Could not get transactions from block', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
	return JSONResponse(data, status_code=status.HTTP_200_OK)

@public_api.get("/get_balance", tags=["Public Routes"])
def get_balance():

	try:
		balance = node.ring[str(node.wallet.address)]['balance'] # Alternative
	except Exception as e:
		print(f"{Fore.YELLOW}get_balance{Fore.RESET}: {Fore.RED}Error: {e}{Fore.RESET}")
		return JSONResponse('Could not get balance', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return JSONResponse({'balance': balance}, status_code=status.HTTP_200_OK)

@public_api.get("/get_temp_balance", tags=["Public Routes"])
def get_temp_balance():
	
	try:
		temp_balance = node.ring[str(node.wallet.address)]['temp_balance'] # Alternative
	except Exception as e:
		print(f"{Fore.RED}Error get_temp_balance: {e}{Fore.RESET}")
		return JSONResponse('Could not get temp_balance', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)	
	return JSONResponse({'temp_balance': temp_balance}, status_code=status.HTTP_200_OK)

@public_api.get("/get_chain_length", tags=["Public Routes"])
def get_chain_length():
	
	return JSONResponse({'chain_length': len(node.blockchain.chain)}, status_code=status.HTTP_200_OK)

@public_api.get("/get_wallet_transaction_list", tags=["Public Routes"])
def get_wallet_transaction_list():

	try:
		my_transactions = []
		for transaction in node.wallet.transactions:
			if transaction.type_of_transaction == TransactionType.COINS or transaction.type_of_transaction == TransactionType.INITIAL:
				my_transactions.append({
					"sender_address": str(node.ring[str(transaction.sender_address)]['id']),
					"receiver_address": str(node.ring[str(transaction.receiver_address)]['id']),
					"type_of_transaction": str(transaction.type_of_transaction)[16:],
					"amount": str(transaction.amount),
					"nonce": str(transaction.nonce),
					"transaction_id": str(transaction.transaction_id),
				})
			elif transaction.type_of_transaction == TransactionType.STAKE:
				my_transactions.append({
					"sender_address": str(node.ring[str(transaction.sender_address)]['id']),
					"type_of_transaction": str(transaction.type_of_transaction)[16:],
					"amount": str(transaction.amount),
					"nonce": str(transaction.nonce),
					"transaction_id": str(transaction.transaction_id),
				})
			elif transaction.type_of_transaction == TransactionType.MESSAGE:
				my_transactions.append({
					"sender_address": str(node.ring[str(transaction.sender_address)]['id']),
					"receiver_address": str(node.ring[str(transaction.receiver_address)]['id']),
					"type_of_transaction": str(transaction.type_of_transaction)[16:],
					"message": str(transaction.message),
					"amount": str(len(transaction.message)),
					"nonce": str(transaction.nonce),
					"transaction_id": str(transaction.transaction_id),
				})
			else:
				return JSONResponse('Invalid type of transaction', status_code=status.HTTP_400_BAD_REQUEST)
		return JSONResponse({'Wallet transactions': my_transactions}, status_code=status.HTTP_200_OK)

	except Exception as e:
		print(f"{Fore.RED}Error get_transaction_list: {e}{Fore.RESET}")
		return JSONResponse('Could not get transaction list', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@public_api.get("/get_chain", tags=["Public Routes"])
def get_chain():

	data = []
	# Iterate through the blockchain and get the transactions, hash and previous hash and get the validator of each block
	for block in node.blockchain.chain:
		
		# For timestamp
		# Convert the time to a datetime object
		timestamp = datetime.fromtimestamp(block.timestamp)
		# Format the datetime object as a string
		timestamp_string = timestamp.strftime("%Y-%m-%d %H:%M:%S")

		data.append({
			"hash": str(block.hash)[:7],
			"previous_hash": str(block.previous_hash)[:7],
			"validator": str(node.ring[str(block.validator)]['id']),
			"timestamp": timestamp_string,
			"total_fees": str(block.get_total_fees()),
			"transactions": block.get_transactions_from_block(node),
		})
	return JSONResponse(data, status_code=status.HTTP_200_OK)

#Debug routes
@public_api.get("/view_ring", tags=["Public Routes"])
async def view_ring():
	try:
		ring_details = []
		for address, details in node.ring.items():
			ring_details.append({
				"address": address,
				"id": details['id'],
				"ip": details['ip'],
				"port": details['port'],
				"stake": details['stake'],
				"balance": details['balance'],
				"temp_balance": details['temp_balance']
			})
		return JSONResponse(ring_details, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse('Could not get ring details', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@public_api.get("/get_pending_list_length", tags=["Public Routes"])
def get_pending_list_length():

	return JSONResponse({'pending_list_length': len(node.pending_transactions)}, status_code=status.HTTP_200_OK)
