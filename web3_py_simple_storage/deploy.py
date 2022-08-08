import json
from web3 import Web3
from solcx import compile_standard, install_solc
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compile solidity

install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadate", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)


# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connectong to ganache

w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/85bf5fa395e04df99a0bc2a6597c5d17")
)
chain_id = 4
my_address = "0x446A40Cad8561d4D045D4ea2c96a7f25b714BBcA"
private_key = os.getenv("PRIVATE_KEY")

# create contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. build Tx
# 2. Sign tx
# 3. Send tx
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


# working with contract
# contract address
# contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
