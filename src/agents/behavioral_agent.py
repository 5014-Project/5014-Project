"""
BehavioralSegmentationAgent.py

This file contains the implementation of the Behavioral and Segmentation Agent.
The agent segments appliance usage patterns, integrates predictions, and adjusts usage based on demand response.

Usage:
- Segments and prioritizes appliances.
- Integrates with PredictionAgent and DemandResponseAgent for holistic energy management.

Inputs:
- Appliance-level energy consumption data.
- Predictions from the PredictionAgent.

Outputs:
- Prioritized appliance usage list.

Agents Needed:
1. Prediction Agent: Provides predicted energy consumption data.
2. Demand Response Agent: Handles demand response requests.
3. Facilitating Agent: Coordinates communication among agents.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from prediction_agent import PredictionAgent
from demand_response_agent import DemandResponseAgent
from facilitating_agent import FacilitatingAgent

class BehavioralSegmentationAgent:
    def __init__(self, appliance_data, prediction_agent: PredictionAgent, demand_response_agent: DemandResponseAgent, facilitating_agent: FacilitatingAgent, n_clusters=3):
        """
        Initialize the Behavioral and Segmentation Agent.

        Args:
        appliance_data (pd.DataFrame): Historical data on energy consumption of various appliances.
        prediction_agent (PredictionAgent): Instance of PredictionAgent.
        demand_response_agent (DemandResponseAgent): Instance of DemandResponseAgent.
        facilitating_agent (FacilitatingAgent): Instance of FacilitatingAgent.
        n_clusters (int): Number of clusters for segmentation.
        """
        self.appliance_data = appliance_data
        self.prediction_agent = prediction_agent
        self.demand_response_agent = demand_response_agent
        self.facilitating_agent = facilitating_agent
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()

    def collect_and_preprocess_data(self):
        """
        Collect and preprocess appliance data.
        """
        self.data_scaled = self.scaler.fit_transform(self.appliance_data[['Energy_Consumption']])

    def segment_appliance_usage(self):
        """
        Segments and classifies appliance usage patterns.

        Returns:
        pd.DataFrame: Appliance data with assigned segments.
        """
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.appliance_data['Segment'] = kmeans.fit_predict(self.data_scaled)
        return self.appliance_data

    def adjust_appliance_usage(self):
        """
        Adjust appliance usage based on predicted demand and demand response needs.
        """
        predicted_demand = self.prediction_agent.get_predicted_demand()
        if predicted_demand > 80:  # Threshold for demand response
            self.demand_response_agent.send_demand_response(predicted_demand)
            self.facilitating_agent.notify_other_agents("Demand response activated.")

    def prioritize_appliances(self):
        """
        Prioritize appliances based on their segments.

        Returns:
        list: List of appliance priorities.
        """
        priority_list = self.appliance_data.sort_values(by='Segment').to_dict('records')
        return priority_list

    def run(self):
        """
        Main loop for the agent's operation.
        """
        self.collect_and_preprocess_data()
        segmented_data = self.segment_appliance_usage()
        self.adjust_appliance_usage()
        priorities = self.prioritize_appliances()
        print("Appliance Priorities:", priorities)
        self.facilitating_agent.notify_other_agents("Appliance priorities updated.", {"priorities": priorities})

# Example Usage
if __name__ == "__main__":
    # Simulate appliance data
    appliance_data = pd.DataFrame({
        'Appliance': ['AC', 'Fridge', 'Washing Machine', 'Microwave', 'Heater'],
        'Energy_Consumption': [1.2, 0.8, 0.6, 0.5, 1.5]  # kWh
    })

    # Assuming agents are instantiated
    prediction_agent = PredictionAgent()
    demand_response_agent = DemandResponseAgent()
    facilitating_agent = FacilitatingAgent()

    behavioral_agent = BehavioralSegmentationAgent(appliance_data, prediction_agent, demand_response_agent, facilitating_agent)
    behavioral_agent.run()
