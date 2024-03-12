# API Documentation

## Introduction
Welcome to the API documentation for the BlockChat backend. This API allows you to interact with the BlockChat application and perform various actions.

## Getting Started
To get started with the API, you will need to follow these steps:

```bash 
add stuff here
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
Sample Text

#### <span style="color:#63bc86">GET</span> `/api/get_balance`
Sample Text

#### <span style="color:#63bc86">GET</span> `/api/get_temp_balance`
Sample Text

#### <span style="color:#63bc86">GET</span> `/api/get_chain_length`
Sample Text

#### <span style="color:#63bc86">GET</span> `/api/get_chain`
Sample Text

## Internal Endpoints
The following internal endpoints are available in the API in order for the nodes to communicate with each other:

#### <span style="color:#d7bf6c">POST</span> `/receive_ring`
Sample Text

#### <span style="color:#d7bf6c">POST</span> `/get_blockchain`
Sample Text

#### <span style="color:#d7bf6c">POST</span> `/get_transaction`
Sample Text

#### <span style="color:#d7bf6c">POST</span> `/get_block`
Sample Text

#### <span style="color:#d7bf6c">POST</span> `/let_me_in`
Sample Text


## Error Handling
In case of any errors, the API will return appropriate error responses with status codes and error messages.