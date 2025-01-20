# trading_platform.py

"""
Module: Peer-to-Peer Energy Trading Platform

Description:
    This module handles the core functionality of the energy trading platform. It manages the process
    of placing bids, matching supply and demand, and completing transactions between participants. 

Inputs:
    - Energy bids from participants (buy/sell offers)
    - Market data (e.g., energy prices, demand levels)
    - Trading rules (e.g., supply-demand matching criteria)

Outputs:
    - Matched bids (accepted transactions)
    - Transaction details (e.g., amount, price, participants)

Agents Needed:
    - NegotiationAgent: To facilitate agreement and contract initiation
    - FacilitatingAgent: To handle overall coordination of the trading system

"""

import random

class TradingPlatform:
    def __init__(self, participants, energy_prices):
        """
        Initializes the trading platform.

        :param participants: List of agents participating in the trading platform.
        :param energy_prices: Dictionary of current energy prices (e.g., per kWh).
        """
        self.participants = participants
        self.energy_prices = energy_prices
        self.active_trades = []

    def place_bid(self, buyer, seller, quantity, price):
        """
        Allows participants to place a bid to buy or sell energy.

        :param buyer: The agent purchasing energy.
        :param seller: The agent selling energy.
        :param quantity: The amount of energy to be traded (in kWh).
        :param price: The price per kWh.
        :return: Confirmation message or error message.
        """
        if buyer.balance >= price * quantity:
            transaction = {
                'buyer': buyer,
                'seller': seller,
                'quantity': quantity,
                'price': price,
                'status': 'Pending'
            }
            self.active_trades.append(transaction)
            return f"Bid placed: Buyer {buyer} wants to buy {quantity} kWh at {price} per kWh from {seller}."
        else:
            return f"Insufficient balance to place bid for {quantity} kWh at {price} per kWh."

    def execute_trade(self, transaction):
        """
        Executes a trade between buyer and seller.

        :param transaction: The transaction object to execute.
        :return: Transaction completion message.
        """
        if transaction['buyer'].balance >= transaction['price'] * transaction['quantity']:
            transaction['buyer'].balance -= transaction['price'] * transaction['quantity']
            transaction['seller'].balance += transaction['price'] * transaction['quantity']
            transaction['status'] = 'Completed'
            return f"Trade completed: {transaction['buyer']} bought {transaction['quantity']} kWh from {transaction['seller']}."
        else:
            return "Insufficient funds to execute trade."

    def match_trades(self):
        """
        Matches available energy bids between buyers and sellers based on price and quantity.
        """
        for trade in self.active_trades:
            if trade['status'] == 'Pending':
                self.execute_trade(trade)

if __name__ == '__main__':
    # Example usage (simulate energy trading platform)
    participants = ['Buyer 1', 'Seller 1', 'Buyer 2', 'Seller 2']
    energy_prices = {'electricity': 0.15}  # $ per kWh
    trading_platform = TradingPlatform(participants, energy_prices)
    
    # Place bids
    print(trading_platform.place_bid('Buyer 1', 'Seller 1', 10, 0.15))
    print(trading_platform.place_bid('Buyer 2', 'Seller 2', 5, 0.20))

    # Match trades
    trading_platform.match_trades()
