from ipaddress import ip_network, IPv4Address
from fastapi import Request, status
from fastapi.responses import JSONResponse
import time

#Initialize CIDR range for internal access
INTERNAL_CIDR = '10.0.0.0/24'
internal_network = ip_network(INTERNAL_CIDR)

async def restrict_internal_routes(request: Request, call_next):
    client_ip = IPv4Address(request.client.host)

    if client_ip not in internal_network:
        return JSONResponse({'error': f'Access denied for IP {client_ip}'}, status_code=status.HTTP_400_BAD_REQUEST)

    return await call_next(request)

async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response