from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException



class Wallet():

    # Nested class Btc inside Wallet class for Bitcoin-specific functionality.
    class Btc:

        # Initialization method for the Btc class.
        def __init__(self, user, password, wallet_name, host="127.0.0.1", port=8332):
            self.conn = None  # Initialize connection variable to None.

            # Attempt to connect to the Bitcoin node using the provided parameters.
            self.connect(user=user, password=password, wallet_name=wallet_name, host=host, port=port)

            # Retrieve the list of incoming transactions.
            self.txs = self.get_incoming_transactions()

        # Method to connect to the Bitcoin node.
        def connect(self, user, password, wallet_name, host, port):
            try:

                # Create a connection to the Bitcoin node using AuthServiceProxy.
                self.conn = AuthServiceProxy(f"http://{user}:{password}@{host}:{port}")

                try:

                    # Try to create the specified wallet.
                    self.create_wallet(wallet_name)
                except:
                    try:

                        # If the wallet creation fails, attempt to load the wallet.
                        self.load_wallet(wallet_name)

                    except Exception as ex:
                        print(f"Error loading wallet: {ex}")
                        return None
                    
                return self.conn
            
            except Exception as ex:
                print(f"Error connecting to Bitcoin node: {ex}")
                return None

        # Method to load an existing wallet.
        def load_wallet(self, wallet_name):
            try:
                result = self.conn.loadwallet(wallet_name)
                return result
            except Exception as ex:
                print(f"Error loading wallet: {ex}")
                return None

        # Method to check if a wallet exists.
        def wallet_exist(self, wallet_name):
            try:
                wallets = self.conn.listwallets()
                return wallet_name in wallets
            except Exception as ex:
                print(f"Error retrieving wallet list: {ex}")
                return False

        # Method to create a new wallet.
        def create_wallet(self, wallet_name):
            try:
                self.conn.createwallet(wallet_name)
            except JSONRPCException as ex:
                pass

        # Retrieve a list of incoming transactions.
        def get_incoming_transactions(self):
            try:
                transactions = self.conn.listtransactions("*", 15000)
                incoming_transactions = [tx for tx in transactions if tx['category'] == 'receive' and tx['confirmations'] > 0]
                return incoming_transactions
            except Exception as ex:
                print(f"Error retrieving transactions: {ex}")
                return None

        # Retrieve blockchain-related information.
        def get_blockchain_info(self):
            try:
                return self.conn.getblockchaininfo()
            except JSONRPCException as ex:
                print(f"Error calling getblockchaininfo: {ex}")

        # Retrieve the balance of a specified account or the entire wallet.
        def get_balance(self, account=None, minconf=1):
            try:
                if account is None:
                    return self.conn.getbalance()
                else:
                    return self.conn.getbalance(account, minconf)
            except JSONRPCException as ex:
                print(f"Error calling getbalance: {ex}")

        # List unspent transactions within a certain range of confirmations.
        def list_unspent(self, minconf=1, maxconf=9999999):
            try:
                return self.connection.listunspent(minconf, maxconf)
            except JSONRPCException as ex:
                print(f"Error calling listunspent: {ex}")

        # Estimate transaction fee based on desired confirmation target and estimate mode.
        def estimate_fee_per_byte(self, conf_target=6, estimate_mode='CONSERVATIVE'):
            try:
                fee_estimate = self.conn.estimatesmartfee(conf_target, estimate_mode)
                fee_rate_satoshi_per_byte = fee_estimate['feerate'] * 100000000 / 1000
                return fee_rate_satoshi_per_byte
            except Exception as ex:
                print(f"Error estimating fee: {ex}")
                return None

        # Send Bitcoin to a specified address.
        def send_to_address(self, recipient_address, amount_btc, subtractfeefromamount=True):
            try:
                txid = self.conn.sendtoaddress(recipient_address, amount_btc, "", "", subtractfeefromamount)
                return txid
            except Exception as ex:
                print(f"Error sending BTC: {ex}")
                return False

        # Generate a new address for receiving payments.
        def get_new_address(self, label='', address_type='bech32'):
            try:
                new_address = self.conn.getnewaddress(label, address_type)
                return new_address
            except Exception as ex:
                print(f"Error generating new address: {ex}")
                return None
            
        # Retrieve the balance for a specific address.
        def get_address_balance(self, address):
            try:

                # Attempt to filter transactions for the specified address.
                tx = [i for i in self.txs if i.get('address') == address][0]
                amount = tx["amount"]
                confirmations = tx["confirmations"]
            except:

                # If the address isn't found in the transactions, set amount to None and confirmations to 0.
                amount = None
                confirmations = 0
                
            # If the amount is not None, return it along with the confirmations.
            if amount != None:
                return {"amount": amount, "confirmations": confirmations}
            else:

                # Check if the transaction is in the mempool (not yet confirmed).
                is_in_mempool = self.get_unconfirmed_transaction_amount(address)
                if is_in_mempool != None:
                    return {"amount": is_in_mempool, "confirmations": 0}
                
                # If the address isn't in the mempool either, return amount as 0.
                return {"amount": 0, "confirmations": confirmations}
    
        # Method to retrieve the number of confirmations for a specific transaction.
        def get_transaction_confirmations(self, txid):
            try:

                # Get transaction info for the given transaction ID.
                transaction_info = self.conn.gettransaction(txid)

                # Return the number of confirmations.
                return transaction_info['confirmations']
            except Exception as ex:
                print(f"Error retrieving transaction info for {txid}: {ex}")
                return None

        # Method to retrieve incoming transactions.
        def get_incoming_transactions(self):
            try:

                # List all transactions with a limit of 10,000.
                transactions = self.conn.listtransactions("*", 10000)

                # Filter for incoming transactions with at least one confirmation.
                incoming_transactions = [tx for tx in transactions if tx['category'] == 'receive' and tx['confirmations'] > 0]
                return incoming_transactions
            except Exception as ex:
                print(f"Error retrieving transactions: {ex}")
                return None

        # Method to get the unconfirmed transaction amount for a specific address.
        def get_unconfirmed_transaction_amount(self, address):
            try:

                # Retrieve the list of transaction IDs in the mempool (unconfirmed transactions).
                mempool_txids = self.conn.getrawmempool()
                
                # Loop over each transaction ID.
                for txid in mempool_txids:

                    # Get the raw transaction data for the transaction ID.
                    raw_tx = self.conn.getrawtransaction(txid)

                    # Decode the raw transaction data to a readable format.
                    decoded_tx = self.conn.decoderawtransaction(raw_tx)
                    
                    # Check if the specified address is a recipient in the transaction.
                    for i in decoded_tx["vout"]:
                        try:
                            address_tx = i["scriptPubKey"]["address"]
                            if address_tx == address:
                                # If the address is found, return the value sent to it.
                                return i["value"]
                        except:
                            pass

                # If no unconfirmed transaction involves the specified address, return None.
                return None
            
            except Exception as ex:
                print(f"Error retrieving unconfirmed transaction amount: {ex}")
                return None








