from colorama import Fore, Style
import textwrap
import os
import re

WIDTH = 66

def brand():
    print(f"""{Fore.GREEN}
    /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\ 
   ( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )
    > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ < 
    /\_/\ .______    __        ______     ______   ______  __    __       ___   .___________.  /\_/\ 
   ( o.o )|   _  \  |  |      /  __  \   /      | /      ||  |  |  |     /   \  |           | ( o.o )
    > ^ < |  |_)  | |  |     |  |  |  | |  ,----'|  ,----'|  |__|  |    /  ^  \ `---|  |----`  > ^ < 
    /\_/\ |   _  <  |  |     |  |  |  | |  |     |  |     |   __   |   /  /_\  \    |  |       /\_/\ 
   ( o.o )|  |_) |  |  `----.|  `--'  | |  `----.|  `----.|  |  |  |  /  _____  \   |  |      ( o.o )
    > ^ < |______/  |_______| \______/   \______| \______||__|  |__| /__/     \__\  |__|       > ^ < 
    /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\  /\_/\ 
   ( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )( o.o )
    > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ <  > ^ < 
    {Fore.RESET}""")
    
def draw_block(block):

    def fix_spaces(string):
        clean_string = re.sub(r'\x1b\[[0-9;]*m', '', string)
        return " " * (WIDTH - 1 - len(clean_string))
    
    def print_block_header_field(key, value):
        print(f"    │ {Fore.GREEN}{key}{Fore.RESET}: {Style.BRIGHT}{value}{Style.RESET_ALL}{fix_spaces(key + ': ' + value)}│")

    def print_transaction_field(key, value):
        # Determine the maximum width available for the value
        max_text_width = WIDTH - len(f"{key}: ") - 6 

        # Split the value into lines with word wrapping
        wrapped_lines = textwrap.wrap(str(value), width=max_text_width)

        # Print each wrapped line
        for i,line in enumerate(wrapped_lines):
            if i == 0:
                print(f"    │     {Fore.BLUE}{key}{Fore.RESET}: {Style.BRIGHT}{line}{Style.RESET_ALL}{fix_spaces(str(key) + ': ' + line + '    ')}│")
            else:
                print(f"    │     {Style.BRIGHT}{line}{Style.RESET_ALL}{fix_spaces(line + '    ')}│")
    transaction_colors = {
        "Initial Transaction": Fore.RED,
        "Coins Transfer": Fore.CYAN,
        "Message": Fore.MAGENTA,
        "Stake": Fore.YELLOW,
        "Genesis": Fore.GREEN
    }
    
    # Draw the block
    print(f"    ┌{WIDTH * '─'}┐")
    print_block_header_field("Block", block['hash'])
    print(f"    ├{WIDTH * '─'}┤")
    print_block_header_field("Previous Hash", block['previous_hash'])
    print(f"    ├{WIDTH * '─'}┤")
    print_block_header_field("Timestamp", block['timestamp'])
    print(f"    ├{WIDTH * '─'}┤")
    print_block_header_field("Validator", block['validator'])
    print(f"    ├{WIDTH * '─'}┤")
    print_block_header_field("Total Fees", block['total_fees'])
    print(f"    ├{WIDTH * '─'}┤")
    print(f"    │{' '*((WIDTH - len('Transactions')) // 2)}{Fore.BLUE}Transactions{Fore.RESET}{' '*((WIDTH - len('Transactions')) // 2)}│")
    print(f"    ├{WIDTH * '─'}┤")
    
    for i, transaction in enumerate(block["transactions"]):
        transaction_type = transaction['type']
        color = transaction_colors.get(transaction_type, Fore.RESET)
        
        print_transaction_field("Transaction Type", color+transaction_type)
        print_transaction_field("Sender", transaction['sender_id'])

        if transaction_type in ["Initial Transaction", "Coins Transfer"]:
            print_transaction_field("Receiver", transaction['receiver_id'])
            print_transaction_field("Amount", str(transaction['payload']))
        elif transaction_type == "Message":
            print_transaction_field("Receiver", transaction['receiver_id'])
            print_transaction_field("Message", str(transaction['payload']))
            print_transaction_field("Costs", str(len(str(transaction['payload']))))
        elif transaction_type == "Stake":
            print_transaction_field("Stake", str(transaction['payload']))
        elif transaction_type == "Genesis":
            print_transaction_field("Receiver", transaction['receiver_id'])
            print_transaction_field("Amount", str(transaction['payload']))
 
        if i == len(block["transactions"]) - 1:
            print("    └──────────────────────────────────────────────────────────────────┘")
        else:
            print("    ├++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++┤")
    
    return

def draw_blockchain(blockchain_data):
    
    def draw_chain():
        chain = f"""{Fore.LIGHTBLUE_EX}                    ┌───│───┐
                    │       │
                    │       │
                    └───│───┘
                    ┌───│───┐   
                    │       │
                    │       │
                    └───│───┘
                    ┌───│───┐   
                    │       │
                    │       │
                    └───│───┘    {Fore.RESET}"""
        print(chain)
    
    brand()
    print("\n    ⛓️ BlockChat Blockchain ⛓️\n")
    
    # Draw the blockchain
    for i,block in enumerate(blockchain_data):
        
        draw_block(block)
        
        if (i == len(blockchain_data) - 1):
            print("\n    Here is a visual representation of the blockchain")
            print("    Scroll above to see the details of each block\n\n")
            break
        draw_chain()
  
def clear_terminal():
    os.system('cls||clear')