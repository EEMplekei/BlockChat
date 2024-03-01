import random

sample_dict = {
    'address1': {
        'id': 1,
        'ip': '192.168.1.1',
        'port': 8080,
        'stake': 1000,
        'balance': 500,
        'temp_balance': 500
    },
    'address2': {
        'id': 2,
        'ip': '192.168.1.2',
        'port': 9090,
        'stake': 1,
        'balance': 1000,
        'temp_balance': 1000
    },
    'address3': {
        'id': 3,
        'ip': '192.168.1.3',
        'port': 7070,
        'stake': 1,
        'balance': 750,
        'temp_balance': 750
    },
    'address4': {
        'id': 4,
        'ip': '192.168.1.4',
        'port': 6060,
        'stake': 1,
        'balance': 600,
        'temp_balance': 600
    },
    'address5': {
        'id': 5,
        'ip': '192.168.1.5',
        'port': 5050,
        'stake': 1,
        'balance': 900,
        'temp_balance': 900
    },
    'address6': {
        'id': 6,
        'ip': '192.168.1.6',
        'port': 4040,
        'stake': 1,
        'balance': 800,
        'temp_balance': 800
    },
    'address7': {
        'id': 7,
        'ip': '192.168.1.7',
        'port': 3030,
        'stake': 0,
        'balance': 550,
        'temp_balance': 550
    },
    'address8': {
        'id': 8,
        'ip': '192.168.1.8',
        'port': 2020,
        'stake': 1000,
        'balance': 650,
        'temp_balance': 650
    },
    'address9': {
        'id': 9,
        'ip': '192.168.1.9',
        'port': 1010,
        'stake': 0,
        'balance': 700,
        'temp_balance': 700
    },
    'address10': {
        'id': 10,
        'ip': '192.168.1.10',
        'port': 1111,
        'stake': 1000,
        'balance': 850,
        'temp_balance': 850
    }
}

class PoSProtocol:
    def __init__(self, seed=None):
        self.staker_nodes = []
        self.cumulative_stakes = []
        self.total_stake = 0
        self.seed = seed
    
    def add_node_to_round(self):
        for address, node in sample_dict.items():
            if node['stake'] > 0:
                self.staker_nodes.append((address, node['id'],node['stake']))
                self.total_stake += node['stake']
                self.update_cumulative_stakes()

    def update_cumulative_stakes(self):
        cumulative_stake = 0
        self.cumulative_stakes = []
        for node in self.staker_nodes:
            cumulative_stake += node[2]  # Assuming stake is the third element in the tuple
            self.cumulative_stakes.append(cumulative_stake)


    def select_validator(self):
        if not self.cumulative_stakes:
            return None
        
        random.seed(self.seed)
        selected_stake = random.randint(1, self.total_stake)
        for i, stake in enumerate(self.cumulative_stakes):
            if selected_stake <= stake:
                return self.staker_nodes[i]


# Create an instance of PoSProtocol
protocol = PoSProtocol()

# Add nodes to the round
protocol.add_node_to_round()

# Print the staker nodes
print("Staker Nodes:", protocol.staker_nodes)

# Select a validator
selected_validator = protocol.select_validator()
print("Selected Validator:", selected_validator)
