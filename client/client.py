import inquirer
import os
import time
import argparse
import requests
from requests.exceptions import RequestException
import json

from texttable import Texttable

# ARGUMENTS
argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
argParser.add_argument("--ip", help="IP of the host")
args = argParser.parse_args()
# Address of node
ip_address = args.ip
port = args.port
address= 'http://' + str(ip_address) + ':' + str(port) 


# Command Line Interface client
def client():
    os.system('cls||clear')
    while(True):
        menu = [ 
            inquirer.List('menu', 
            message= "BlockChat Client", 
            choices= ['💸 New transaction', '💬 New message', '🎰 Set Stake','📦 View last block', '💰 Show balance', '💁 Help', '🌙 Exit'], 
            ),
        ]
        choice = inquirer.prompt(menu)['menu']
        os.system('cls||clear')


        # NEW TRANSACTION CLIENT CALL ========================================
        if choice == '💸 New transaction':
            questions = [
                inquirer.Text(name='recipent', message ='🍀 What is the Recipent ID of the lucky one?'),
                inquirer.Text(name='amount', message = '🪙 How many BlockChat coins to send?'),
            ]
            answers = inquirer.prompt(questions)
            recipent = str(answers['recipent'])
            amount = str(answers['amount'])  
            print('Sending ' + amount + ' BlockChat Coins to client with ID ' + str(answers['recipent']) + '...')
            try:
                # api client call  
                response = requests.get(address+'/api/create_transaction/'+recipent+'/'+amount)
                data = response.json()
                print(data)
            except requests.exceptions.HTTPError:
                if (data):
                    print(data)
                else:
                    print("Node is not active. Try again later.")
            input("Press any key to go back...")
            os.system('cls||clear')
            continue


        # NEW MESSAGE CLIENT CALL ========================================
        if choice == '💬 New message':
            questions = [
                inquirer.Text(name='recipent', message ='🍀 What is the Recipent ID of the lucky one?'),
                inquirer.Text(name='message', message = 'What is the message?'),
            ]
            answers = inquirer.prompt(questions)
            recipent = str(answers['recipent'])
            message = str(answers['message'])  
            print('Sending message: "' + message + '" to client with ID ' + str(answers['recipent']) + '...')
            try:
                # api client call  for message

                ## NEEDS MODS
                response = requests.get(address+'/')
                data = response.json()
                print(data)
            except requests.exceptions.HTTPError:
                if (data):
                    print(data)
                else:
                    print("Node is not active. Try again later.")
            input("Press any key to go back...")
            os.system('cls||clear')
            continue


        # SET STAKE CLIENT CALL ========================================
        if choice == '🎰 Set Stake':
            questions = [
                inquirer.Text(name='stake', message ='🎰 How much do you want to stake?'),
            ]
            answers = inquirer.prompt(questions)
            stake = str(answers['stake'])

            print('Staking ' + stake + ' BlockChat Coins in order to be in the next lottery...')

            try:
                # api client call to stake
                response = requests.get(address+'/api/...'+stake)
                data = response.json()
                print(data)
            except requests.exceptions.HTTPError:
                if (data):
                    print(data)
                else:
                    print("Node is not active. Try again later.")
            input("Press any key to go back...")
            os.system('cls||clear')
            continue
        
        
        # VIEW LAST BLOCK CLIENT CALL ========================================
        if choice == '📦 View last block':
            try:
                # api client call to view last block
                response = requests.get(address+'/')
                try:
                    data = response.json()                
                    table = Texttable()
                    table.set_deco(Texttable.HEADER)
                    table.set_cols_dtype(['t', 't', 't'])
                    table.set_cols_align(["c", "c", "c"])
                    rows = []
                    rows.append(["Sender ID", "Receiver ID", "Amount"])
                    for line in data:
                        rows.append(list(line.values()))
                    table.add_rows(rows)
                    print(table.draw() + "\n")
                except:
                    print("Validated block not available yet. Try again later")
            except requests.exceptions.HTTPError:
                print("Node is not active. Try again later.")
            input("Press any key to go back...")
            os.system('cls||clear')
            continue


        # SHOW BALANCE CLIENT CALL ========================================
        if choice == '💰 Show balance':
            try:
                response = requests.get(address+'/api/get_balance')
                try:
                    data = response.json()                
                    print(data)
                except:
                    print("Validated block not available yet. Try again later")
            except requests.exceptions.HTTPError:
                print("Node is not active. Try again later.")
            input("Press any key to go back...")
            os.system('cls||clear')
            continue

        # HELP =======================================
        if choice == '💁 Help':
            os.system('cls||clear')
            print('💸 New transaction:')
            print('Send transaction to a node. Select node id and amount.\n\n')

            print('💬 New message:')
            print('Send a message to a node. Select node id and message.\n\n')

            print('🎰 Set Stake:')
            print('Set the stake for the client wallet.\n\n')

            print('📦 View last block:')
            print('View the last block in the blockchain.\n\n')

            print('💰 Show balance')
            print('View the balance of the client from the client wallet.\n\n')

            input("Press any key to go back...")
            os.system('cls||clear')
            break

        # EXIT =======================================
        if choice == '🌙 Exit':
            os.system('cls||clear')
            print("We will miss you 💋")
            time.sleep(0.7)
            os.system('cls||clear')
            break
client()