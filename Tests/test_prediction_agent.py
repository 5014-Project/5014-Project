# test_prediction_agent.py

"""
Module: Test Suite for Prediction Agent

Description:
    This module contains unit tests for the Prediction Agent, which is responsible for predicting 
    energy demand based on historical data and forecasting models. The tests validate the prediction
    accuracy and functionality of the agent's methods.

Inputs:
    - Test inputs for energy consumption data and time-series predictions

Outputs:
    - Assert the correctness of prediction logic, forecast accuracy, and edge cases

Agents Needed:
    - PredictionAgent: The agent being tested
"""

import unittest
from agents.prediction_agent import PredictionAgent

class TestPredictionAgent(unittest.TestCase):
    def setUp(self):
        """
        Set up the initial conditions for the tests.
        """
        self.prediction_agent = PredictionAgent()

    def test_get_predicted_demand(self):
        """
        Test the functionality of get_predicted_demand method.
        """
        predicted_demand = self.prediction_agent.get_predicted_demand()
        self.assertIsInstance(predicted_demand, float)
        self.assertGreater(predicted_demand, 0)

    def test_forecast_accuracy(self):
        """
        Test the prediction accuracy of energy demand forecast.
        """
        # Assuming we have some known dataset to test the prediction accuracy
        self.assertGreater(self.prediction_agent.evaluate_forecast_accuracy(), 0.9)

if __name__ == "__main__":
    unittest.main()
