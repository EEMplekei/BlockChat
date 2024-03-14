from functools import wraps
from colorama import Fore

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