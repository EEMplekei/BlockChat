# BlockChat
A blockchain from scratch built for the purposes of the course Distributed Systems ([School of Electrical and Computer Engineering NTUA](https://www.ece.ntua.gr)). 

<br/>
<img src="https://cdn-icons-png.flaticon.com/512/2152/2152539.png" alt="blocks" height="250"/>

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
python3 client.py --node n
```
> [!IMPORTANT]  
> n: The node on which you want to connect to

For other operating systems different than Linux-Debian you will have to fill in the gaps 

## High Level Software Description 🔍

#### Genesis Block
The Genesis block is the first block of the blockchain and  it is the only block that does not get validated. The genesis block has only 1 transaction that is (TOTAL_NODES*1000) Coins to Bootstrap Node.

#### Initial State



#### Create Transaction

Text should be added here 


#### Moving from Block 1 to many Blocks

Text should be added here 

#### Proof of Stake Protocol

Text should be added here 

## Testing 🔬
To run the given transactions from the txt files [here](./testing/). Do the following:

```bash
cd BlockChat/testing
python3 run_tests.py -t test
```
> [!IMPORTANT]  
> test: Test to be run. (eg 0 --> trans0.txt)

- `trans0.txt` : Transactions that are made from node0
- `trans1.txt` : Transactions that are made from node1
- `trans2.txt` : Transactions that are made from node2
- `trans3.txt` : Transactions that are made from node3
- `trans4.txt` : Transactions that are made from node4
- `trans5.txt` : Transactions that are made from node5
- `trans6.txt` : Transactions that are made from node6
- `trans7.txt` : Transactions that are made from node7
- `trans8.txt` : Transactions that are made from node8
- `trans9.txt` : Transactions that are made from node9
