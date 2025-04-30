# test change for git


# Write a program which creates an account for each person, and then creates transactions between the accounts.
# The person in the 'From' column is paying money, so the amount needs to be deducted from their account.
# The person in the 'To' column is being paid, so the amount needs to be added to their account.

# Your program should support two commands, which can be typed in on the console:
# -> List All should output the names of each person, and the total amount they owe, or are owed.
# -> List [Account] should also print a list of every transaction, with the date and narrative, for that account with that name.

import csv
import logging
import datetime
import json
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)
logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

logger.info('logging started.')


class Account:
    def __init__(self, name):
        self.name = name
        self.balance = 0.0
        self.transactions = []

    def __str__(self):
        return f"{self.name}: £{self.balance:.2f}"

    def addTransaction(self, transaction: dict):
        if transaction['From'] == self.name:
            self.balance -= transaction['Amount']
        elif transaction['To'] == self.name:
            self.balance += float(transaction['Amount'])
        else:
            logger.error(f"Transaction does not belong to account {self.name}: {transaction}")
        
        self.transactions.append(transaction)

    def listTransactions(self):
        for transaction in self.transactions:
            if transaction['From'] == self.name:
                print(f"{transaction['Date']}: -£{transaction['Amount']:.2f}, {transaction['Narrative']}")
            elif transaction['To'] == self.name:
                print(f"{transaction['Date']}: +£{transaction['Amount']:.2f}, {transaction['Narrative']}")


def loadFile(filename):
    if filename.endswith('.csv'):    
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            transactions = [row for row in reader]
    elif filename.endswith('.json'):
        with open(filename, 'r') as jsonfile:
            transactions = json.load(jsonfile)
    # elif filename.endswith('.xml'):
    #     tree = ET.parse(filename)
    #     root = tree.getroot()
    #     transactions = []
    #     for transaction in root:
    #         transaction_data = {
    #             'Date': transaction.find('Date').text,
    #             'From': transaction.find('From').text,
    #             'To': transaction.find('To').text,
    #             'Amount': transaction.find('Value').text,
    #             'Narrative': transaction.find('Description').text
    #         }
    #         transactions.append(transaction_data)
    else:
        logger.error(f"Unsupported file format: {filename}")
        return None

    accounts = {}

    for i, transaction in enumerate(transactions):
        if filename.endswith('.json'):
            transaction['From'] = transaction.pop('FromAccount')
            transaction['To'] = transaction.pop('ToAccount')

        if transaction['From'] not in accounts:
            account = Account(transaction['From'])
            accounts[transaction['From']] = account
        if transaction['To'] not in accounts:
            account = Account(transaction['To'])
            accounts[transaction['To']] = account

        try:
            if filename.endswith('.csv'):
                transaction['Date'] = datetime.datetime.strptime(transaction['Date'], '%d/%m/%Y').date()
            elif filename.endswith('.json'):
                transaction['Date'] = datetime.datetime.strptime(transaction['Date'], '%Y-%m-%dT%H:%M:%S').date()
        except ValueError:
                logger.error(f"Invalid date '{transaction['Date']}' in line {i}, transaction: {transaction}")
                continue

        try:
            transaction['Amount'] = float(transaction['Amount'])
        except ValueError:
            logger.error(f"Invalid amount '{transaction['Amount']}' in line {i}, transaction: {transaction}")
            continue

        accounts[transaction['From']].addTransaction(transaction)
        accounts[transaction['To']].addTransaction(transaction)

    logger.info(f"Transactions loaded successfully from '{filename}'.")
    return accounts


def mergeAccounts(accounts1, accounts2):
    for account in accounts2:
        if account in accounts1:
            accounts1[account].balance += accounts2[account].balance
            accounts1[account].transactions.extend(accounts2[account].transactions)
        else:
            accounts1[account] = accounts2[account]

    return accounts1


def getUserCommand():
    return input("Commands available:\n" \
                 "-> Import File [filename] to import a file.\n" \
                 "-> List All to see all accounts and the total amount they owe/are owed.\n" \
                 "-> List [Account] to print a list of every transaction for that account.\n")


def supportBank():
    accounts = {}

    while True:
        stringInput = getUserCommand()
        if stringInput.startswith("List"):
            try:
                findAccount = stringInput.partition(" ")[2]
                if findAccount == "All":
                    for account in accounts:
                        print(accounts[account])
                elif findAccount in accounts:
                    print(accounts[findAccount])
                    accounts[findAccount].listTransactions()
                else:
                    print(f"Account '{findAccount}' not found.")
            except:
                logger.error(f"Error processing command: {stringInput}")
            
        elif stringInput.startswith("Import File"):
            try:
                filename = stringInput.split(" ")[-1]
                newAccounts = loadFile(filename)
                if newAccounts:
                    accounts = mergeAccounts(accounts, newAccounts)
                    print(f"File '{filename}' imported successfully.")
                else:
                    print(f"Failed to import file '{filename}'.")
                    logger.error(f"Failed to import file '{filename}'.")
            except Exception as e:
                logger.error(f"Error importing file: {e}")
            
        elif stringInput.lower() == "exit":
            break

        else:
            print("Invalid command. Please try again.")
            logger.info(f"Invalid command. User input: {stringInput}")


if __name__ == "__main__":
    logger.info('program started.')
    supportBank()