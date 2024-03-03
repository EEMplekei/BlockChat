from enum import Enum
from hashlib import sha256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ( padding, utils)
from cryptography.hazmat.primitives import serialization
from cryptography import exceptions
from colorama import Fore

class TransactionType(Enum):
	COINS = 1
	MESSAGE = 2

class Transaction:

	sender_address = None                               # public key of sender wallet
	receiver_address = None                             # public key of receiver wallet
	type_of_transaction : TransactionType = None        # type of transaction (coins, message)
	amount = None										# amount of coins to send (if type is coins)
	message = None										# message to send (if type is message)
	nonce = None                                        # nonce for transaction
	transaction_id = None                               # ID of transaction
	signature = None                                    # signature that proves sender owns the private key
	
	#Constructor, take only the sa, ra, type of transaction and payload
	def __init__(self, sender_address, receiver_address, type_of_transaction: TransactionType, payload, nonce):
					
		#Check valid type and payload
		if type_of_transaction == TransactionType.COINS:
			if not ((isinstance(payload, (int, float))) and (payload > 0)):
				raise ValueError("Transaction amount must be a positive number")
			self.amount = payload                           # amount of coins to send
			self.message = None
		elif type_of_transaction == TransactionType.MESSAGE:
			if not isinstance(payload, str):
				raise ValueError("Transaction message must be a string")
			self.amount = None
			self.message = payload                          # message to send
		else:
			raise ValueError("Invalid transaction type")

		#Check valid nonce
		if not (isinstance(nonce, int) and nonce > 0):
			raise ValueError("Nonce must be an integer")

		self.sender_address = sender_address				# pk of wallet of sender
		self.receiver_address = receiver_address            # pk of wallet of receiver
		self.type_of_transaction = type_of_transaction      # type of transaction (coins, message)
		self.nonce = nonce                                  # nonce for transaction
		

	#Equality operator overloading (==)
	def __eq__(self, other):
		if not isinstance(other, Transaction):
			return False
		return self.__dict__ == other.__dict__
	
	#Representation function overloading
	def __repr__(self):
		return f"Transaction(sender_address={self.sender_address}, receiver_address={self.receiver_address}, type_of_transaction={self.type_of_transaction}, payload={self.amount or self.message}, nonce={self.nonce}, transaction_id={self.transaction_id}, signature={self.signature})"

	#Dictionary function overloading
	def to_dict(self):
		return self.__dict__
	
	#Hash function calculation
	def calculate_hash(self):
	
		data_to_hash = ''.join([
		str(self.sender_address),
		str(self.receiver_address),
		str(self.type_of_transaction),
		str(self.amount),
		str(self.message),
		str(self.nonce)
		])

		self.transaction_id = sha256(data_to_hash.encode()).digest()

	#Sign transaction hash with private key
	#Mentioned in the original Satoshi Nakamoto's paper (bitcoin), we calculate the hash of the transaction and sign it with the private key of the sender
	def sign_transaction(self, private_key):
		
		#Check if the private key matches the sender address
		pub_from_priv_key = private_key.public_key().public_bytes(
					encoding=serialization.Encoding.PEM,
					format=serialization.PublicFormat.SubjectPublicKeyInfo
		)
		if pub_from_priv_key != self.sender_address:
			raise ValueError("Private key does not match the sender address")

		#Check if the transaction has been hashed
		if self.transaction_id is None:
			self.calculate_hash()

		self.signature = private_key.sign(
			self.transaction_id,
			padding.PSS(
				mgf=padding.MGF1(hashes.SHA256()),
				salt_length=padding.PSS.MAX_LENGTH
			),
			utils.Prehashed(hashes.SHA256())
		)
		
	#Verify the received transaction (based on the signature)
	def verify_signature(self, public_key):

		if self.signature is None:
			raise ValueError("No signature found in the transaction")

		try:
			public_key = serialization.load_pem_public_key(public_key)
			public_key.verify(
				self.signature,
				self.transaction_id,
				padding.PSS(
					mgf=padding.MGF1(hashes.SHA256()),
					salt_length=padding.PSS.MAX_LENGTH
				),
				utils.Prehashed(hashes.SHA256())
			)
			return True
		except exceptions.InvalidSignature:
			print("Transaction not validated : Invalid signature")
			return False
		except Exception as e:
			print("Transaction not validated : ", e)
			return False

	#Validate the transaction (based on the signature and the sender's balance)
	def validate_transaction(self, sender_balance):

		#Recalculate the hash of the transaction because it might have been tampered with by a malicious sender
		self.calculate_hash()
		
		if(not self.verify_signature(self.sender_address)):
			print(f"{Fore.YELLOW}validate_transaction{Fore.RESET}: {Fore.RED}Transaction not validated, not valid signature{Fore.RESET}")
			return False
		
		transaction_cost = (self.amount if self.type_of_transaction == TransactionType.COINS else len(self.message))
		if(transaction_cost > sender_balance):
			print(f"{Fore.YELLOW}validate_transaction{Fore.RESET}: {Fore.RED}Transaction not validated, not enough coins{Fore.RESET}")
			return False
				
		return True