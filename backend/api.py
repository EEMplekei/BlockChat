from fastapi import FastAPI
from colorama import Fore
import uvicorn

try:
	# from helper_functions.api_middleware import restrict_internal_routes, add_process_time_header
	from controllers.internal_api import internal_api
	from controllers.public_api import public_api
	from controllers.shared_recourses import node
except ImportError as e:
	print(f"{Fore.RED}Could not import required classes{Fore.RESET}")
	input("Press any key to exit...")
	exit()

app = FastAPI()

app.mount(path = "/api", app = public_api)
app.mount(path = "", app = internal_api)

# WEB SERVER RUN
uvicorn.run(app, host = None, port = int(node.port))
