# test_negotiation_agent.py

"""
Module: Test Suite for Negotiation Agent

Description:
    This module contains unit tests for the Negotiation Agent, which is responsible for facilitating
    auction-based negotiation for energy trading between micro-grids. The tests validate the functionality
    of energy trading, auction processes, and negotiation logic.

Inputs:
    - Test inputs for negotiation parameters and auction bids

Outputs:
    - Assert the correctness of negotiation, bid handling, and auction outcomes

Agents Needed:
    - NegotiationAgent: The agent being tested
"""

import unittest
from agents.negotiation_agent import NegotiationAgent

class TestNegotiationAgent(unittest.TestCase):
    def setUp(self):
        """
        Set up the initial conditions for the tests.
        """
        self.negotiation_agent = NegotiationAgent()

    def test_initiate_auction(self):
        """
        Test the initiation of an auction.
        """
        auction_id = self.negotiation_agent.initiate_auction(100, 200)
        self.assertEqual(auction_id, 1)

    def test_process_bid(self):
        """
        Test processing bids in an auction.
        """
        bid_response = self.negotiation_agent.process_bid(1, 150)
        self.assertTrue(bid_response)

if __name__ == "__main__":
    unittest.main()
