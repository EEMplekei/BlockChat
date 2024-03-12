from colorama import Fore

def brand():
	print(f"""{Fore.GREEN}
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
	chain = f"""{Fore.LIGHTBLUE_EX}
				┌───│───┐
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
				└───│───┘
{Fore.RESET}"""
	print(chain)

def fix_spaces(string):
	return " " * (65 - len(string))

def draw_blockchain(blockchain_data):
	brand()
	print()
	print("    ⛓️ BlockChat Blockchain ⛓️")
	print()
	# Draw the blockchain
	for i,block in enumerate(blockchain_data):
		
		line = "Block:  "+block['hash']+""
		print(f"    ┌──────────────────────────────────────────────────────────────────┐")
		print(f"    │ {Fore.GREEN}{line}{Fore.RESET}{fix_spaces(line)}│")
		print(f"    ├──────────────────────────────────────────────────────────────────┤")
		line = "Previous Hash: "+block['previous_hash']+""
		print(f"    │ {Fore.GREEN}{line}{Fore.RESET}{fix_spaces(line)}│")  
		print(f"    ├──────────────────────────────────────────────────────────────────┤")
		line = "Validator: "+block['validator']+""
		print(f"    │ {Fore.GREEN}{line}{Fore.RESET}{fix_spaces(line)}│")
		line = "Total Fees: "+block['total_fees']+""
		print(f"    │ {Fore.GREEN}{line}{Fore.RESET}{fix_spaces(line)}│")
		for transaction in block["transactions"]:
			print(f"    ├++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++┤")
			line = "Transaction Details"
			print(f"    │ {Fore.LIGHTMAGENTA_EX}{line}{Fore.RESET}{fix_spaces(line)}│")
			line = "Transaction Type: "+transaction['type']+""
			print(f"    │    {Fore.LIGHTBLUE_EX}{line}{Fore.RESET}{fix_spaces('   '+line+'')}│")
			line = "Sender: "+transaction['sender_id']+""
			print(f"    │    {Fore.LIGHTBLUE_EX}{line}{Fore.RESET}{fix_spaces('   '+line+'')}│")
			line = "Receiver: "+transaction['receiver_id']+""
			print(f"    │    {Fore.LIGHTBLUE_EX}{line}{Fore.RESET}{fix_spaces('   '+line+'')}│")
			

			line = "Payload: "+str(transaction['payload'])+""
			# if line is too long, split it into multiple lines
			if len(line) > 65:
				# first line
				print(f"    │    {Fore.LIGHTBLUE_EX}{line[:61]}{Fore.RESET}{fix_spaces(line[:61])}│")
				
				line = line[61:]
				while len(line) > 65:
					# middle lines
					print(f"    │    {Fore.LIGHTBLUE_EX}{line[:61]}{Fore.RESET}{fix_spaces(line[:61])}│")
					line = line[61:]
				# last line
				print(f"    │    {Fore.LIGHTBLUE_EX}{line}{Fore.RESET}{fix_spaces('   '+line+'')}│")

			else:
				print(f"    │    {Fore.LIGHTBLUE_EX}{line}{Fore.RESET}{fix_spaces('   '+line+'')}│")
		print("    └──────────────────────────────────────────────────────────────────┘")
		
		if (block == blockchain_data[len(blockchain_data) - 1]):
			print()
			print("    Here is a visual representation of the blockchain")
			print("    Scroll above to see the details of each block")
			print()
			print()
			break
		draw_chain()