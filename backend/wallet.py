from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Wallet:
 
	# Initialize a wallet (generate_wallet)
	def __init__(self):
		self.public_key, self.private_key = self.generate_rsa_key_pair()
		self.transactions = []

	def generate_rsa_key_pair(self):
		
		private_key = rsa.generate_private_key(
			public_exponent = 65537,
			key_size = 2048
		)

		public_key = private_key.public_key()

		return public_key, private_key