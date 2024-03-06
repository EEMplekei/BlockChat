from colorama import Fore
import argparse
import socket
import fcntl
import struct

#Parse the arguments and return the IP and port
def get_ip_and_port():

	argParser = argparse.ArgumentParser()
	argParser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
	argParser.add_argument("-i", "--interface", help="Interface on which the node is running")
	args = argParser.parse_args()

	try:
		ip = get_ip_linux(args.interface)
	except OSError:
		print(f"{Fore.YELLOW}get_ip_and_port{Fore.RESET}: {Fore.RED}Could not get the IP address of interface {args.interface}{Fore.RESET}")
		exit()
	port = args.port

	if port is None:
		print(f"{Fore.YELLOW}get_ip_and_port{Fore.RESET}: {Fore.RED} Could not get provided{Fore.RESET}")
		exit()
  
	return ip, str(port)

#Get the IPv4 address of a specific interface
def get_ip_linux(interface: str) -> str:

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	packed_iface = struct.pack('256s', interface.encode('utf_8'))
	packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
	return socket.inet_ntoa(packed_addr)