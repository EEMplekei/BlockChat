from colorama import Fore

def brand():
    print(f"""{Fore.YELLOW}
            /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\ 
            ( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )
            > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ < 
            /\_/\ .______    __        ______     ______   ______  __    __       ___   .___________.  /\_/\ 
            ( o.o )|   _  \  |  |      /  __  \   /      | /      ||  |  |  |     /   \  |           | ( o.o )
            > ^ < |  |_)  | |  |     |  |  |  | |  ,----'|  ,----'|  |__|  |    /  ^  \ `---|  |----`  > ^ < 
            /\_/\ |   _  <  |  |     |  |  |  | |  |     |  |     |   __   |   /  /_\  \    |  |       /\_/\ 
            ( o.o )|  |_)  | |  `----.|  `--'  | |  `----.|  `----.|  |  |  |  /  _____  \   |  |      ( o.o )
            > ^ < |______/  |_______| \______/   \______| \______||__|  |__| /__/     \__\  |__|       > ^ < 
            /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\ 
            ( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )
            > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ < 
    {Fore.RESET}""")


def draw_chain():
    chain = f"""{Fore.CYAN}
                        ┌───│───┐
                        │       │
                        │       │
                        │       │
                        └───│───┘
                        ┌───│───┐   
                        │       │
                        │       │
                        │       │
                        └───│───┘
                        ┌───│───┐   
                        │       │
                        │       │
                        │       │
                        └───│───┘
{Fore.RESET}"""
    print(chain)


def draw_blockchain(blockchain_data):
    brand()
    for i,block in enumerate(blockchain_data):
        print(f"    ┌──────────────────────────────────────────────────────────────────┐")
        print(f"    │ {Fore.GREEN}Block {i}:  {block['hash']} {Fore.RESET}│")
        print(f"    ├──────────────────────────────────────────────────────────────────┤")
        print(f"    │ {Fore.GREEN}Previous Hash: {block['previous_hash']} {Fore.RESET}      │")  
        print(f"    ├──────────────────────────────────────────────────────────────────┤")
        print(f"    │ {Fore.GREEN}Validator: {block['validator']} {Fore.RESET}         │")
        for transaction in block["transactions"]:
            print(f"    ├++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++┤")
            print(f"    │   {Fore.LIGHTMAGENTA_EX} Transaction Type: {transaction['type']} {Fore.RESET}   │") 
            print(f"    ├──────────────────────────────────────────────────────────────────┤")
            print(f"    │   {Fore.LIGHTMAGENTA_EX} Sender: {transaction['sender_id']} {Fore.RESET} │") 
            print(f"    ├──────────────────────────────────────────────────────────────────┤")
            print(f"    │   {Fore.LIGHTMAGENTA_EX} Receiver: {transaction['receiver_id']} {Fore.RESET} │")
            print(f"    ├──────────────────────────────────────────────────────────────────┤")
            print(f"    │   {Fore.LIGHTMAGENTA_EX} Amount: {transaction['amount']} {Fore.RESET} │")
        print("    └──────────────────────────────────────────────────────────────────┘")
        if (block == blockchain_data[len(blockchain_data) - 1]):
            break
        draw_chain()
    

# Sample blockchain data
blockchain_data = [
    {
        "hash": "hash1",
        "previous_hash": "0",
        "validator": "validator1",
        "transactions": [
            {"type": "Coins Transfer", "sender_id": "sender1", "receiver_id": "receiver1", "amount": 10},
            {"type": "Coins Transfer", "sender_id": "sender2", "receiver_id": "receiver2", "amount": 5}
        ]
    },
    {
        "hash": "hash2",
        "previous_hash": "hash1",
        "validator": "validator2",
        "transactions": [
            {"type": "Coins Transfer", "sender_id": "sender3", "receiver_id": "receiver3", "amount": 7},
            {"type": "Coins Transfer", "sender_id": "sender4", "receiver_id": "receiver4", "amount": 3}
        ]
    },
    {
        "hash": "hash3",
        "previous_hash": "hash2",
        "validator": "validator3",
        "transactions": [
            {"type": "Coins Transfer", "sender_id": "sender5", "receiver_id": "receiver5", "amount": 12},
            {"type": "Coins Transfer", "sender_id": "sender6", "receiver_id": "receiver6", "amount": 8}
        ]
    }
]