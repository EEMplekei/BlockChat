# Command Line Interface (CLI) 👨‍💻

## Use Cases

#### New transaction 💸
Transfer Coins to another wallet

#### New message 💬
Send a message to another user

#### Set Stake 🎰
Set your stake for the Proof of Stake protocol

> [!NOTE]  
> The Proof of Stake (PoS) protocol calculates the validator for the current block based on a probabilistic algorithm in which every node has a probability of becoming the validator proportional to the last stake of that node in a validated block. This means that the stake you declare on block _i_ will account for the probability of becoming the validator of block _i+1_.

#### View last block 📦

Get a visual representation of the last block

#### View blockchain ⛓️

Get a visual representation of the whole blockchain

#### Show balance 💰

Get the wallet balance in the last validated block

#### Help 💁

Detailed explanation of the above

#### Exit 🌙

Exit the client

## Run CLI

```bash
python3 client.py --node n
```
> [!IMPORTANT]  
> _n_: The name node on which you want to connect to. as written in the nodes_config.json file
>
> Each line represents a node. It should be in the form `{node_name}: {public_ip:port},` where _public\_ip:port_ is the IP|port pair on which the API of the node awaits for requests.
