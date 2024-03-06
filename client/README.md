# Command Line Interface (CLI) 👨‍💻

## Use Cases

#### New transaction 💸
Transfer Coins to another wallet

#### New message 💬
Send a message to another user

#### Set Stake 🎰
Set your stake for the Proof of Stake protocol

> [!INFO]  
> The Proof of Stake (PoS) protocol calculates the validator for the current block based on a probabilistic algorithm in which every node has a probability of becoming the validator proportional to the last stake in the last validated block. This means that the stake you declare on block i will account for the probability of becoming the validator of block i+1.

#### View last block 📦

Get a visual representation of the last block

#### View blockchain ⛓️

Get a visual representation of the hole blockchain

#### Show balance 💰

Get the node balance in the last validated block

#### Help 💁

Detailed explanation of the above

#### Exit 🌙


## Run CLI

```bash
python3 client.py --node n
```
> [!IMPORTANT]  
> n: The node on which you want to connect to