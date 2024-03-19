import os
import json

# Function to clear the terminal
def clear_terminal():
    os.system('cls||clear')

# Function to get the address of the nodes
def get_nodes_address(nodes):
    f = open('../nodes_config.json')
    nodes_config = json.load(f)
    f.close()
    address = []
    # Networking Configuration
    for node_number in range(nodes):
        temp = nodes_config.get(f'node{node_number}') if node_number in range(10) else print("Invalid node number") and exit()
        address.append(temp)
    print("✅ Addresses of the nodes obtained ✅")
    return address