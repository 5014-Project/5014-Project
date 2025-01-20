"""
AuctionModel.py

This file contains the implementation of a Trustful Double Auction model for Peer-to-Peer (P2P) energy trading.
The model facilitates secure and efficient trading between interconnected micro-grids, addressing supply-demand imbalances.

Usage:
- The auction model processes bids and offers from market participants.
- It ensures fair and efficient trade execution using trust and auction theory principles.

Inputs:
- Bids: Energy purchase requests with specified prices and quantities.
- Offers: Energy sale offers with specified prices and quantities.

Outputs:
- Matched trades: Finalized transactions between buyers and sellers.
- Market balance reports: Summary of trading outcomes and adjustments for supply-demand imbalances.
"""

class TrustfulDoubleAuction:
    def __init__(self):
        """
        Initializes the Trustful Double Auction model.
        """
        self.bids = []   # List to store incoming bids
        self.offers = [] # List to store incoming offers

    def add_bid(self, buyer, price, quantity):
        """
        Adds a new bid to the auction.

        Args:
        buyer (str): Identifier for the buyer.
        price (float): Offered price per unit of energy.
        quantity (int): Quantity of energy requested.
        """
        self.bids.append({'buyer': buyer, 'price': price, 'quantity': quantity})
        print(f"Bid added: {buyer} wants {quantity} units at {price} per unit.")

    def add_offer(self, seller, price, quantity):
        """
        Adds a new offer to the auction.

        Args:
        seller (str): Identifier for the seller.
        price (float): Asking price per unit of energy.
        quantity (int): Quantity of energy offered.
        """
        self.offers.append({'seller': seller, 'price': price, 'quantity': quantity})
        print(f"Offer added: {seller} offers {quantity} units at {price} per unit.")

    def match_trades(self):
        """
        Matches bids and offers using a double auction mechanism.

        The matching process respects trust, price, and quantity constraints to ensure fairness and efficiency.
        """
        print("Matching trades...")
        self.bids.sort(key=lambda x: -x['price'])  # Sort bids descending by price
        self.offers.sort(key=lambda x: x['price']) # Sort offers ascending by price

        while self.bids and self.offers:
            bid = self.bids[0]
            offer = self.offers[0]

            if bid['price'] >= offer['price']:
                matched_quantity = min(bid['quantity'], offer['quantity'])
                print(f"Match found: {bid['buyer']} buys {matched
