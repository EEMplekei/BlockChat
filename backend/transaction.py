# TRANSACTION 

import Crypto
import Crypto.Random

from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5

class Transaction:

    def __init__(self, sender_address, sender_private_key, receiver_address, type_of_transaction, amount, message, nonce, transaction_id, signature):
        #Initialize a new transaction (create_transaction)
        self.sender_address = sender_address                # public key of wallet of sender
        self.receiver_address = receiver_address            # public key of wallet of receiver
        self.type_of_transaction = type_of_transaction      # type of transaction (coins, message)
        self.amount = amount                                # amount of coins to send
        self.message = message                              # message to send
        self.transaction_id = self.calculate_hash()         # ID of transaction          
        self.signature = None                               # signature that proves sender owns the private key

    def calculate_hash(self):
        #Calculate hash of transaction and use it as its ID
        self.transaction_id = Crypto.Random.get_random_bytes(128).decode("ISO-8859-1")
        return

    def to_dict(self):
        #Convert transaction object to dictionary for readability.
        dict = {
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "type_of_transaction" : self.type_of_transaction,
            "amount" : self.amount,
            "message" : self.message,
            "transaction_id" : self.transaction_id,
            "signature" : self.signature
        }
        return dict

    def sign_transaction(self, private_key):
        #Sign transaction with private key
        # self.signature = PKCS1_v1_5.new(rsa_key=private_key).sign(self)
        return
    
    def verify_signature(self):
        #Verify signature of sender (private, public keys)
        try:
            # PKCS1_v1_5.new(self.sender_address).verify(self.transaction_id, self.signature)
            return True
        except (ValueError, TypeError):
            return False

    def validate_transaction(self, id, UTXOs):
        #Verify signature of sender + 
        #Verify sender has enough amount to spend
        balance = 0
        for utxo in UTXOs[id]:
             balance += utxo.amount

             
        if (not self.verify_signature()):
            print("❌ Transaction NOT Validated : Not valid address")
            return False
        
        # elif(ring[str(self.sender_address)]['balance'] < self.amount ):
        #     print("❌ Transaction NOT Validated : Not enough coins")
        #     return False

        elif(balance < self.amount):
            print("❌ Transaction NOT Validated : Not enough coins")
            return False
        
        else: 
            print("✅ Transaction Validated !")
            return True