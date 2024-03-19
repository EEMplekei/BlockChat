from functools import wraps
from colorama import Fore
from utils.env_variables import TOTAL_NODES
from fastapi.responses import JSONResponse
from fastapi import status

# Call once function to ensure that genesis block is only created once
def call_once(func):
	def wrapper(*args, **kwargs):
		if not wrapper.called:
			wrapper.called = True
			return func(*args, **kwargs)
		else:
			raise RuntimeError("Function can only be called once.")
	
	wrapper.called = False
	return wrapper

# Bootstrap required function to ensure that a function is only called on the bootstrap node
def bootstrap_required(func):
	@wraps(func)
	def wrapper(self, *args, **kwargs):
		if self.is_bootstrap:
			return func(self, *args, **kwargs)
		else:
			print(f"{Fore.RED}Function can only be called on the bootstrap node.{Fore.RESET}")
			raise RuntimeError("Function can only be called on the bootstrap node.")
	return wrapper

# Check if the ring is full
def check_ring_full(node):
	def decorator(func):
		@wraps(func)
		async def wrapper(*args, **kwargs):
			if len(node.ring) < TOTAL_NODES:
				return JSONResponse('Ring is not full yet', status_code=status.HTTP_400_BAD_REQUEST)
			return await func(*args, **kwargs)
		return wrapper
	return decorator