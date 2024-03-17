from utils import utils, drawers
import json

# Opening JSON file
with open('nodes_config.json') as f:
	nodes_config = json.load(f)
	
#Parse arguments
node = utils.parse_arguments()

# Networking Configuration
address = utils.get_node_address(nodes_config, node)

if not utils.check_api_availability(address, node):
		exit()

#Clear terminal and show brand name
drawers.clear_terminal()
drawers.brand()

while(True):
	choice = utils.get_user_choice(node)
	drawers.clear_terminal()
	utils.handle_user_choice(choice, address, node)