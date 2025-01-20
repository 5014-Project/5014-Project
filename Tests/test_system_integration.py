# test_system_integration.py

"""
Module: Integration Test Suite for the Entire Energy Management System

Description:
    This module contains integration tests to verify the communication and coordination between
    all agents in the energy management system. It ensures that data flows correctly between components
    and that the overall system performs as expected.

Inputs:
    - Test scenarios involving multiple agents' interactions

Outputs:
    - Validating system integration, performance, and successful coordination between agents

Agents Needed:
    - All agents: PredictionAgent, DemandResponseAgent, BehavioralSegmentationAgent,
      NegotiationAgent, FacilitatingAgent
"""

import unittest
from agents.prediction_agent import PredictionAgent
from agents.demand_response_agent import DemandResponseAgent
from agents.behavioral_agent import BehavioralSegmentationAgent
from agents.negotiation_agent import NegotiationAgent
from agents.facilitating_agent import FacilitatingAgent

class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        """
        Set up the initial conditions for the integration tests.
        """
        self.prediction_agent = PredictionAgent()
        self.demand_response_agent = DemandResponseAgent()
        self.behavioral_agent = BehavioralSegmentationAgent()
        self.negotiation_agent = NegotiationAgent()
        self.facilitating_agent = FacilitatingAgent()

    def test_system_integration(self):
        """
        Test the interaction and data flow between all agents in the system.
        """
        predicted_demand = self.prediction_agent.get_predicted_demand()
        self.assertIsInstance(predicted_demand, float)

        self.demand_response_agent.send_demand_response(predicted_demand)
        self.assertEqual(self.demand_response_agent.demand_threshold, 80)

        result = self.behavioral_agent.adjust_appliance_usage()
        self.assertTrue(result)

        auction_id = self.negotiation_agent.initiate_auction(100, 200)
        self.assertEqual(auction_id, 1)

        system_status = self.facilitating_agent.check_system_status()
        self.assertTrue(system_status)

if __name__ == "__main__":
    unittest.main()
