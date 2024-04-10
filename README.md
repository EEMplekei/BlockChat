# BlockChat
A blockchain from scratch built for the purposes of the course Distributed Systems ([School of Electrical and Computer Engineering NTUA](https://www.ece.ntua.gr)). 

<br/>
<img src="https://cdn-icons-png.flaticon.com/512/2152/2152539.png" alt="blocks" height="250"/>

## Exploring the Repo 🔍

``` bash
BlockChat
├── nodes_config.json               # Addresses of all nodes
├── README.md                    
├── requirements.txt                # Python pip requirements
├── backend                         # Folder containing backend node code
│   ├── api.py                      # API Code for one node
│   ├── .env                        # Env variables of blockchain
│   ├── README.md
│   ├── components                  
│   │   ├── blockchain.py           # Blockchain class along with some methods 
│   │   ├── block.py                # Block class along with some methods 
│   │   ├── node.py                 # Node class along the major methods of the system
│   │   ├── proof_of_stake.py       # POS class along with some methods 
│   │   ├── transaction.py          # Transaction class along with some methods 
│   │   └── wallet.py               # Wallet class along with some methods 
│   ├── routes
│   │   ├── internal_api.py         # All endpoints made to be called from other nodes in the system
│   │   └── public_api.py           # All endpoints made to be called from an external client
│   └── utils                       # Utils folder containing functions used in API
│       ├── env_variables.py        
│       ├── middleware.py           
│       ├── network.py              
│       └── wrappers.py
├── client
│   ├── client.py                   # Main client file that implements the client features
│   ├── README.md           
│   └── utils                       # Utils folder containing functions used in client.py
│       ├── drawers.py
│       ├── handlers.py
│       └── utils.py
├── deploy                          # Deploy scripts for both GNOME terminal and MAC terminal
│   ├── execute_okeanos_gnome.sh
│   └── mac_run_all.sh
├── testing                         # Testing folder (only used for benchmarking)
│   ├── output.txt                  # In this file we write the benchmarking after each test
│   ├── run_tests.py                # Script that runs the tests with equal staking (all 10)
│   ├── unfair_test.py              # Script that runs the tests with unfair staking (all 10 except one --> 100)
│   ├── draw_graphs.py              # Reads output.txt and generates graphs
│   ├── test_inputs                 # Folder containing dummy messages for the tests to run
│   │   ├── nodes_10                # Dummy messages for 10 node deployment
│   │   │   ├── ...
│   │   └── nodes_5                 # Dummy messages for 5 node deployment
│   │       ├── ...
│   └── utils                       # Utils folder containing functions and routines used in tests
│       ├── routines.py
│       └── utils.py
└── VPP                             # Detailed documentation with UML
    └── BlockChat.vpp
```

## Installation 🖥️
The deployment process (for Linux-Debian) is described below:

##### First Clone the github repository
```bash
git clone git@github.com:EEMplekei/BlockChat.git
```

#### Install requirements
```bash
sudo apt install python3
sudo apt install pip3
cd BlockChat
pip3 install -r requirements.txt
```

#### Run the [API](./backend/README.md) (you have to do this in every node of the blockchain)

##### Deploy the nodes

For OKEANOS Deployment do the following:

```bash
cd BlockChat/deploy

# For GNOME Terminal
bash execute_okeanos_gnome.sh 5 10 # for 5 node deployment with block size 10

# For Mac Teminal
bash mac_run_all.sh 5 10 # for 5 node deployment with block size 10
```

Detailed API documentation is implemented in OpenAPI 3.0 specifications and you can view the routes and calls in Swagger 

[API DOCUMENTATION SWAGGER HERE](https://app.swaggerhub.com/apis-docs/EEMplekei/BlockChatAPI/0.1.0)



#### Run the [CLI](./client/README.md) (in order create and see transactions among other things)
```bash
cd BlockChat
python3 client.py --node node0
```


For other operating systems different than Linux-Debian you will have to fill in the gaps 


## Testing 🔬
To run the given transactions from the txt files [here](./testing/). Do the following:


#### Fair Testing

```bash
cd BlockChat/testing
python3 run_tests.py -n 5 -b 10     # for testing 5 nodes with block_size 10  
```

#### Unfair Testing

```bash
cd BlockChat/testing
python3 unfair_test.py    # automatically runs only for 5 nodes with block_size 5 (from project requirements)
```

