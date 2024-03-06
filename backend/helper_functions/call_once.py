
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