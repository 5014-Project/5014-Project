"""
PredictionAgent.py

This file contains the implementation of the Prediction Agent for the Smart Home Energy Management System.
The agent uses machine learning models (LSTM) to predict energy production and consumption for smart homes.

Usage:
- This agent interacts with other agents to provide forecasts of energy production and consumption.
- It utilizes historical data to make hourly predictions.

Inputs:
- Historical energy production and consumption data.
- Weather data and user behavior patterns (optional).

Outputs:
- Predicted energy production and consumption.
- Forecast reports for use by other agents (e.g., Demand Response Agent, Negotiation Agent).

Agents Needed:
1. Facilitating Agent: For coordinating communication and overall system management.
"""

import numpy as np
import LSTM_Model  # Assuming LSTM_Model.py provides an LSTM model implementation

class PredictionAgent:
    def __init__(self, facilitating_agent, model_path="lstm_model.h5"):
        """
        Initializes the Prediction Agent with a reference to the Facilitating Agent and an LSTM model.

        Args:
        facilitating_agent (FacilitatingAgent): Instance of the Facilitating Agent for system-wide communication.
        model_path (str): Path to the pre-trained LSTM model.
        """
        self.facilitating_agent = facilitating_agent
        self.model = LSTM_Model.load_model(model_path)

    def predict(self, input_data):
        """
        Predicts energy production and consumption using the LSTM model.

        Args:
        input_data (np.array): Array of historical data for making predictions.

        Returns:
        dict: Dictionary containing predicted production and consumption.
        """
        prediction = self.model.predict(input_data)
        production, consumption = prediction[:, 0], prediction[:, 1]
        print(f"Predicted production: {production}, Predicted consumption: {consumption}")
        return {
            "production": production.tolist(),
            "consumption": consumption.tolist()
        }

    def run(self, input_data):
        """
        Main method to run the Prediction Agent.

        Args:
        input_data (np.array): Array of historical data for making predictions.
        """
        prediction_results = self.predict(input_data)
        # Notify other agents of prediction results
        self.facilitating_agent.notify_other_agents("Prediction results are ready.", prediction_results)

# Example usage
facilitating_agent = FacilitatingAgent()  # Assuming FacilitatingAgent is implemented as shown earlier
prediction_agent = PredictionAgent(facilitating_agent)

# Example input data (random data for demonstration)
input_data = np.random.rand(24, 2)  # 24-hour historical data with production and consumption
prediction_agent.run(input_data)
