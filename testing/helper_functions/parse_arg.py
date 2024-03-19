from argparse import ArgumentParser
from colorama import Fore

#Parse command line arguments
def parse_arguments():
	try:
		arg_parser = ArgumentParser()
		arg_parser.add_argument("-n", "--nodes", help="Number of nodes in the test", required = True)
		args = arg_parser.parse_args()
		return args.nodes
	except Exception as e:
		print(f"{Fore.YELLOW}parse_arguments: {Fore.RED}{e}{Fore.RESET}")
		exit(-1)