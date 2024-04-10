# API Documentation

## Introduction
Welcome to the API documentation for the BlockChat backend. This API allows you to interact with the BlockChat application and perform various actions.

## Getting Started
To get started with the API, you will need to follow these steps:

```bash
cd BlockChat/backend
python3 api.py -i eth0 -p 8000
```

## API Endpoints
The following endpoints are available in the API:

#### <span style="color:#d7bf6c">POST</span> `/api/create_transaction`

```javascript
request.body = {
    "receiver_id": int,
    "payload": str,
    "type_of_transaction": str
}
```

#### <span style="color:#d7bf6c">POST</span> `/api/set_stake`

Maybe should do it in string
```javascript
request.body = {
    "stake": str
}
```

#### <span style="color:#63bc86">GET</span> `/api/view_last_block`

#### <span style="color:#63bc86">GET</span> `/api/get_balance`

#### <span style="color:#63bc86">GET</span> `/api/get_temp_balance`

#### <span style="color:#63bc86">GET</span> `/api/get_chain_length`

#### <span style="color:#63bc86">GET</span> `/api/get_chain`

## Internal Endpoints
The following internal endpoints are available in the API in order for the nodes to communicate with each other:

#### <span style="color:#d7bf6c">POST</span> `/receive_ring`

#### <span style="color:#d7bf6c">POST</span> `/receive_blockchain`

#### <span style="color:#d7bf6c">POST</span> `/receive_transaction`

#### <span style="color:#d7bf6c">POST</span> `/receive_block`

#### <span style="color:#d7bf6c">POST</span> `/join_request`

## Error Handling
In case of any errors, the API will return appropriate error responses with status codes and error messages.
