from enum import Enum
from hashlib import sha256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import exceptions
from cryptography.hazmat.primitives import serialization
from wallet import Wallet

class TransactionType(Enum):
	COINS = 1
	MESSAGE = 2

class Transaction:

	sender_address = None                               # public key of sender wallet
	receiver_address = None                             # public key of receiver wallet
	type_of_transaction : TransactionType = None        # type of transaction (coins, message)
	payload = None                                      # amount of coins or message
	nonce = None                                        # nonce for transaction
	transaction_id = None                               # ID of transaction
	signature = None                                    # signature that proves sender owns the private key
	
	#Constructor, take only the sa, ra, type of transaction and payload
	def __init__(self, sender_address, receiver_address, type_of_transaction: TransactionType, payload, nonce):
		
		#Check if the sender and receiver addresses are strings (they might not be public key but we don't check that here, it will throw an error later if it's not a public key)
		if(not isinstance(sender_address, str)):
			raise ValueError("Sender address must be a string")
		if(not isinstance(receiver_address, str)):
			raise ValueError("Receiver address must be a string")


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

		if not (isinstance(nonce, int) and nonce > 0):
			raise ValueError("Nonce must be an integer")

		self.sender_address = sender_address				# pk of wallet of sender
		self.receiver_address = receiver_address            # pk of wallet of receiver
		self.type_of_transaction = type_of_transaction      # type of transaction (coins, message)
		self.nonce = nonce                                  # nonce for transaction
		
		self.calculate_hash()

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
		self.transaction_id = sha256((str(self.sender_address) + str(self.receiver_address) + str(self.type_of_transaction) + str(self.amount) + str(self.message) + str(self.nonce)).encode()).hexdigest()

	#Sign transaction hash with private key
	#Mentioned in the original Satoshi Nakamoto's paper (bitcoin), we calculate the hash of the transaction and sign it with the private key of the sender
	def sign_transaction(self, private_key):

		pem = private_key.public_key().public_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PublicFormat.SubjectPublicKeyInfo
		)
		print(pem)
  
		pem1 = self.sender_address.public_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PublicFormat.SubjectPublicKeyInfo
		)
		print(pem1)
		print(pem == pem1)
		print(private_key.public_key() == self.sender_address)
		if private_key.public_key() != self.sender_address:
			raise ValueError("Private key does not match the sender address")
		elif self.transaction_id is None:
			self.calculate_hash()
		self.signature = private_key.sign(
			self.calculate_hash,
			padding.PSS(
				mgf=padding.MGF1(hashes.SHA256()),
				salt_length=padding.PSS.MAX_LENGTH
			),
			hashes.SHA256()
		)
	
	#Verify the received transaction
	def verify_signature(self, public_key):
		#Verify signature of sender (private, public keys)
		try:
			public_key.verify(
				self.signature,
				self,
				padding.PSS(
					mgf=padding.MGF1(hashes.SHA256()),
					salt_length=padding.PSS.MAX_LENGTH
				),
				hashes.SHA256()
			)
			return True
		except InvalidSignature:
			return False

	# def validate_transaction(self, id, UTXOs):
	#     #Verify signature of sender + 
	#     #Verify sender has enough amount to spend
	#     balance = 0
	#     for utxo in UTXOs[id]:
	#          balance += utxo.amount

			 
	#     if (not self.verify_signature()):
	#         print("❌ Transaction NOT Validated : Not valid address")
	#         return False
		
	#     # elif(ring[str(self.sender_address)]['balance'] < self.amount ):
	#     #     print("❌ Transaction NOT Validated : Not enough coins")
	#     #     return False

	#     elif(balance < self.amount):
	#         print("❌ Transaction NOT Validated : Not enough coins")
	#         return False
		
	#     else: 
	#         print("✅ Transaction Validated !")
	#         return True

wallet_sender = Wallet()
wallet_receiver = Wallet()

transaction1 = Transaction(wallet_sender.public_key, wallet_receiver.public_key, TransactionType.COINS, 10, 69)
transaction1.sign_transaction(wallet_receiver.private_key)
# transaction1.sign_transaction(wallet.private_key)

