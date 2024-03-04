import random

class PoSProtocol:
    def __init__(self, seed=None):
        self.staker_nodes = []
        self.total_nodes = []
        self.total_stake = 0
        self.cumulative_stakes = []
        self.staker_nodes_all_zeros = []
        self.seed = seed
    
    def add_node_to_round(self, ring):
        for address, node in ring.items():
            if node['stake'] > 0:
                self.staker_nodes.append((address, node['id'],node['stake']))
                self.total_stake += node['stake']
                self.update_cumulative_stakes()
            elif node['stake'] == 0:
                self.staker_nodes_all_zeros.append((address, node['id'],node['stake']))


    def update_cumulative_stakes(self):
        cumulative_stake = 0
        self.cumulative_stakes = []
        for node in self.staker_nodes:
            cumulative_stake += node[2]  # Assuming stake is the third element in the tuple
            self.cumulative_stakes.append(cumulative_stake)


    def select_validator(self):
        random.seed(self.seed)
        if not self.cumulative_stakes:
            return random.choice(list(self.staker_nodes_all_zeros))
        
        selected_stake = random.randint(1, self.total_stake)
        for i, stake in enumerate(self.cumulative_stakes):
            if selected_stake <= stake:
                return self.staker_nodes[i]
