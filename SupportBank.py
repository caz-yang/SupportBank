
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

logger = logging.getLogger(__name__)
logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

logger.info('logging started.')

def loadCSVTransactions(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        transactions = [row for row in reader]

    accounts = {}

    for i, transaction in enumerate(transactions):
        if transaction['From'] not in accounts:
            accounts[transaction['From']] = {'balance': 0, 'transactions': []}
        if transaction['To'] not in accounts:
            accounts[transaction['To']] = {'balance': 0, 'transactions': []}

        try:
            accounts[transaction['From']]['balance'] -= float(transaction['Amount'])
            accounts[transaction['To']]['balance'] += float(transaction['Amount'])
        except ValueError:
            logger.error(f"Invalid amount '{transaction['Amount']}' in line {i}, transaction: {transaction}")
            continue

        try:
            transaction['Date'] = datetime.datetime.strptime(transaction['Date'], '%d/%m/%Y').date()
        except ValueError:
            logger.error(f"Invalid date '{transaction['Date']}' in line {i}, transaction: {transaction}")
            continue

        accounts[transaction['From']]['transactions'].append(transaction)
        accounts[transaction['To']]['transactions'].append(transaction)

    return accounts


def mergeAccounts(accounts1, accounts2):
    for account in accounts2:
        if account in accounts1:
            accounts1[account]['balance'] += accounts2[account]['balance']
            accounts1[account]['transactions'].extend(accounts2[account]['transactions'])
        else:
            accounts1[account] = accounts2[account]

    return accounts1


def getUserCommand():
    return input("Commands available:\n" \
    "-> List All to see all accounts and the total amount they owe/are owed.\n" \
    "-> List [Account] to print a list of every transaction for that account.\n")


def listAll(accounts):
    for account in accounts:
        print(f"{account}: {accounts[account]['balance']:.2f}")


def listAccount(accounts, account):
    print(f"{account}: {accounts[account]['balance']:.2f}")
    for transaction in accounts[account]['transactions']:
        if transaction['From'] == account:
            print(f"{transaction['Date']}: -£{transaction['Amount']}, {transaction['Narrative']}")
        else:
            print(f"{transaction['Date']}: +£{transaction['Amount']}, {transaction['Narrative']}")


def supportBank():
    accounts1 = loadCSVTransactions('Transactions2014.csv')
    logger.info('Transactions2014.csv loaded.')
    accounts2 = loadCSVTransactions('DodgyTransactions2015.csv')
    logger.info('DodgyTransactions2015.csv loaded.')
    accounts = mergeAccounts(accounts1, accounts2)
    logger.info('Accounts merged.')

    stringInput = getUserCommand()

    while(True):
        try:
            if stringInput == "List All":
                listAll(accounts)
                stringInput = getUserCommand()
            elif stringInput.lower() == "exit":
                break
            else:
                account = stringInput.partition(" ")[2]
                if account in accounts:
                    listAccount(accounts, account)
                else:
                    print(f"Account '{account}' not found.")
                stringInput = getUserCommand()
        except:
            print("Exception thrown. Invalid input.")
            stringInput = getUserCommand()


if __name__ == "__main__":
    logger.info('program started.')
    supportBank()