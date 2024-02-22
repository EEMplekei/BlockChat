from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class Wallet:

	def __init__(self):
	    # Initialize a wallet (generate_wallet)
		self.private_key = generate_rsa_key_pair()[0]
		self.public_key = generate_rsa_key_pair()[1]
		self.transactions = []


    def generate_rsa_key_pair():
        # Generate a new private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Get the public key from the private key
        public_key = private_key.public_key()

        # Serialize the private key
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize the public key
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_key_pem, public_key_pem