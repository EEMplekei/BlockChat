from colorama import Fore
from helper_functions import parse_input

def expected_balance(number_of_nodes, node):
    if number_of_nodes == 5:
        trans_folder = f'trans5_{node}'
    elif number_of_nodes == 10:
        trans_folder = f'trans10_{node}'
    else: 
        print("Invalid")
        return
    balance = 1000
    receiver_id_list, messages_list = parse_input.parse_input_files(trans_folder)
    for message in messages_list:
        balance -= len(message)
    # Due to staking 10 at the beginning (we are talking about temp_balance, not balance)
    balance -= 10
    return balance


def expected_chain_length(number_of_nodes, blocksize, total_transactions):
    # 2*number_of_nodes-1 is the additional number of transactions that will be sent to the network
    # number_of nodes - 1 for initial transactions 
    # number_of_nodes for the staking transactions
    all_transactions = total_transactions+ 2*number_of_nodes-1
    return (all_transactions  // blocksize) + 1

print(f"{Fore.GREEN}Expected Temp_Balances for 5 NODES{Fore.RESET}")
print()

for i in range(5):
    print(f"Node {i} Expected Temp_Balance: {expected_balance(5, i)}")


print()
print("==============================================")
print(f"{Fore.GREEN}Expected Temp_Balances for 10 NODES{Fore.RESET}")
print()

for i in range(10):
    print(f"Node {i} Expected Temp_Balance: {expected_balance(10, i)}")
