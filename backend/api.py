from fastapi import FastAPI

app = FastAPI()

def create_genesis_block():
    # ! BOOTSTRAP ONLY !
    # Create the first block of the blockchain (GENESIS BLOCK)

    # Create new block
    gen_block = node.create_new_block() # previous_hash autogenerates
    gen_block.nonce = 0

    # Create first transaction
    first_transaction = Transaction(
        sender_address='0', 
        receiver_address = node.wallet.address,
        type_of_transaction = 'coins', 
        amount = total_bbc
        message= "",
        nonce = 0,
        transaction_id = "0",
        signature = "",
    )

    # Add transaction to genesis block
    gen_block.transactions_list.append(first_transaction)
    gen_block.calculate_hash() # void

    # Add genesis block to blockchain
    node.blockchain.chain.append(gen_block)

    # Create new empty block
    node.current_block = node.create_new_block()
    
    return

