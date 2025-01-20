# test_demand_response_agent.py

"""
Module: Test Suite for Demand Response Agent

Description:
    This module contains unit tests for the Demand Response Agent, which is responsible for managing
    the demand response actions by interacting with the grid based on the predicted energy consumption
    and system status. The tests validate the agent’s ability to respond to grid requests.

Inputs:
    - Test inputs for demand thresholds and response actions

Outputs:
    - Validate proper demand response actions and threshold management

Agents Needed:
    - DemandResponseAgent: The agent being tested
"""

import unittest
from agents.demand_response_agent import DemandResponseAgent

class TestDemandResponseAgent(unittest.TestCase):
    def setUp(self):
        """
        Set up the initial conditions for the tests.
        """
        self.demand_response_agent = DemandResponseAgent()

    def test_send_demand_response(self):
        """
        Test the functionality of sending a demand response action.
        """
        response = self.demand_response_agent.send_demand_response(80)
        self.assertEqual(response, "Demand response initiated")

    def test_set_demand_threshold(self):
        """
        Test the ability to set demand thresholds.
        """
        self.demand_response_agent.set_demand_threshold(75)
        self.assertEqual(self.demand_response_agent.demand_threshold, 75)

if __name__ == "__main__":
    unittest.main()
