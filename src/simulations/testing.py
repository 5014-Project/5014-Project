# testing.py

"""
Module: Testing and Validation of the Energy Management System

Description:
    This module includes test cases for individual agents and the overall energy management system. 
    It ensures that each agent behaves correctly and that the system works as expected when integrated.

Inputs:
    - Agent methods and system behaviors (e.g., placing bids, adjusting demand)

Outputs:
    - Test results (pass/fail) for each agent and the overall system

Agents Needed:
    - All agents (PredictionAgent, DemandResponseAgent, BehavioralSegmentationAgent, etc.)
"""

import unittest
from agents.prediction_agent import PredictionAgent
from agents.demand_response_agent import DemandResponseAgent
from agents.behavioral_agent import BehavioralSegmentationAgent
from agents.negotiation_agent import NegotiationAgent
from agents.facilitating_agent import FacilitatingAgent
from system_simulator import SystemSimulator

class TestPredictionAgent(unittest.TestCase):
    def test_predict_demand(self):
        prediction_agent = PredictionAgent()
        predicted_demand = prediction_agent.get_predicted_demand()
        self.assertIsInstance(predicted_demand, float)
        self.assertGreater(predicted_demand, 0)

class TestDemandResponseAgent(unittest.TestCase):
    def test_send_demand_response(self):
        demand_response_agent = DemandResponseAgent()
        result = demand_response_agent.send_demand_response(100)
        self.assertEqual(result, "Demand response activated.")

class TestSystemSimulator(unittest.TestCase):
    def test_simulate_scenario(self):
        agents = {'demand_response_agent': DemandResponseAgent()}
        scenarios = [{'name': 'High Demand', 'demand': 100, 'supply': 80}]
        simulator = SystemSimulator(agents, scenarios)
        simulator.run_simulation()
        results = simulator.get_results()
        self.assertEqual(len(results), 1)
        self.assertIn('High Demand', results[0]['scenario'])

if __name__ == '__main__':
    unittest.main()
