# transaction_history.py

"""
Module: Transaction History for Peer-to-Peer Energy Trading

Description:
    This module tracks and stores transaction records from the energy trading platform. It ensures
    that all trades are logged with relevant details for future reference and audit.

Inputs:
    - Completed transaction details (buyer, seller, price, quantity, etc.)

Outputs:
    - Recorded transaction details
    - Transaction history retrieval

Agents Needed:
    - FacilitatingAgent: To facilitate the recording of transactions.
"""

import pandas as pd

class TransactionHistory:
    def __init__(self):
        """
        Initializes the transaction history manager.
        """
        self.transactions = pd.DataFrame(columns=['Buyer', 'Seller', 'Quantity', 'Price', 'Status'])

    def record_transaction(self, buyer, seller, quantity, price, status='Completed'):
        """
        Records a new energy transaction in the history.

        :param buyer: The agent purchasing energy.
        :param seller: The agent selling energy.
        :param quantity: The amount of energy (in kWh).
        :param price: The price per kWh.
        :param status: The transaction status (default is 'Completed').
        """
        transaction = {
            'Buyer': buyer,
            'Seller': seller,
            'Quantity': quantity,
            'Price': price,
            'Status': status
        }
        self.transactions = self.transactions.append(transaction, ignore_index=True)

    def get_transaction_history(self):
        """
        Returns the entire transaction history.
        """
        return self.transactions

if __name__ == '__main__':
    # Example usage
    transaction_history = TransactionHistory()
    transaction_history.record_transaction('Buyer 1', 'Seller 1', 10, 0.15)
    print(transaction_history.get_transaction_history())
