# BlockChat ⛓️
A blockchain from scratch built for the purposes of the course Distributed Systems ([School of Electrical and Computer Engineering NTUA](https://www.ece.ntua.gr)). 

## Installation 🖥️
The deployment process (for Linux-Debian) is described below:

##### First Clone the github repository
```bash
git clone git@github.com:EEMplekei/BlockChat.git
```

##### Install requirements
```bash
sudo apt install python3
sudo apt install pip3
cd BlockChat/api
pip3 install -r requirements.txt
```

##### Run the [API](./backend/README.md) (you have to do this in every node of the blockchain)
```bash
cd BlockChat/api
python3 api --i eth --port p
```
> [!IMPORTANT]  
> eth: Interface on which the node is running
> p: Port on which the node is running

##### Run the [CLI](./client/README.md) (in order create and see transactions among other things)
```bash
cd BlockChat/client
python3 client.py --domain api_domain --port p
```
> [!IMPORTANT]  
> api_domain: The domain on which the node is running
> p: Port on which the node is running

For other operating systems different than Linux-Debian you will have to fill in the gaps 

## High Level Software Description 🔍

#### Genesis Block

Text should be added here 

#### Initial State

Text should be added here 

#### Create Transaction

Text should be added here 


#### Moving from Block 1 to many Blocks

Text should be added here 

#### Proof of Stake Protocol

Text should be added here 

## Testing 🔬