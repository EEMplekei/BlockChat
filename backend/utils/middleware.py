from ipaddress import ip_network, ip_address
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi import Response
from typing import Callable
from colorama import Fore
from utils.env_variables import INTERNAL_CIDR
import time

#Initialize CIDR range for internal access

try:
    internal_network = ip_network(INTERNAL_CIDR)
except ValueError:
    print(f"{Fore.YELLOW}restrict_internal_routes{Fore.RESET}: {Fore.RED}Invalid CIDR range: {INTERNAL_CIDR}{Fore.RESET}")
    exit()

#Middleware to restrict access to internal routes
async def restrict_internal_routes(request: Request, call_next: Callable) -> Response:
    client_ip = ip_address(request.client.host)
    if not client_ip.is_loopback and client_ip not in internal_network:
        return JSONResponse({'error': f'Access denied for IP {client_ip}'}, status_code=status.HTTP_400_BAD_REQUEST)

    return await call_next(request)

#Middleware to add process time header
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

