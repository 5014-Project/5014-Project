"""
NegotiationAgent.py

This file contains the implementation of the Negotiation Agent for the Smart Home Energy Management System.
The agent manages peer-to-peer (P2P) energy trading between interconnected micro-grids, implementing a trustful double auction model to balance supply and demand.

Usage:
- This agent interacts with other homes/micro-grids to facilitate energy trading.
- It uses auction theory to ensure fair and efficient trading while managing supply-demand imbalances.

Inputs:
- Energy supply and demand data from micro-grids.
- Bids and offers from participants in the energy market.

Outputs:
- Matched trades between buyers and sellers.
- Reports on trading outcomes and market balance.

Agents Needed:
1. Facilitating Agent: For coordinating communication and overall system management.
2. Prediction Agent: For providing energy forecasts to inform trading decisions.
"""

class NegotiationAgent:
    def __init__(self, facilitating_agent):
        """
        Initializes the Negotiation Agent with a reference to the Facilitating Agent.

        Args:
        facilitating_agent (FacilitatingAgent): Instance of the Facilitating Agent for system-wide communication.
        """
        self.market_data = []  # List to store bids and offers
        self.facilitating_agent = facilitating_agent

    def collect_market_data(self, bid, offer):
        """
        Collects bids and offers from market participants.

        Args:
        bid (dict): Dictionary containing bid information (e.g., buyer, price, quantity).
        offer (dict): Dictionary containing offer information (e.g., seller, price, quantity).
        """
        self.market_data.append({'bid': bid, 'offer': offer})
        print("Market data collected.")

    def execute_auction(self):
        """
        Executes the double auction to match bids and offers.

        This method uses auction theory to find optimal matches between buyers and sellers.
        """
        print("Executing double auction...")
        # Simulate auction logic for demonstration purposes
        for transaction in self.market_data:
            bid = transaction['bid']
            offer = transaction['offer']
            if bid['price'] >= offer['price']:
                print(f"Matched: {bid['buyer']} buys {bid['quantity']} units from {offer['seller']} at {offer['price']} per unit.")
            else:
                print("No match found.")

        # Notify the Facilitating Agent of the auction results
        self.facilitating_agent.notify_other_agents("Auction executed, trading results processed.")

    def run(self, bid, offer):
        """
        Main method to run the Negotiation Agent for a single auction cycle.

        Args:
        bid (dict): Dictionary containing bid information.
        offer (dict): Dictionary containing offer information.
        """
        self.collect_market_data(bid, offer)
        self.execute_auction()

# Example usage
facilitating_agent = FacilitatingAgent()  # Assuming FacilitatingAgent is implemented as shown earlier
negotiation_agent = NegotiationAgent(facilitating_agent)

# Example bid and offer data
bid = {'buyer': 'Home1', 'price': 50, 'quantity': 10}
offer = {'seller': 'Home2', 'price': 45, 'quantity': 10}

# Run the Negotiation Agent with example data
negotiation_agent.run(bid, offer)
