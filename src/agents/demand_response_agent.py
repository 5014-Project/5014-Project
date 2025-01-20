"""
DemandResponseAgent.py

This file contains the implementation of the Demand Response Agent for the Smart Home Energy Management System.
The agent interacts with various other agents to manage energy demand during peak load periods through demand response mechanisms.

Usage:
- This agent continuously monitors for demand response requests from the grid.
- It uses predictions from the Prediction Agent to plan curtailment actions.
- It adjusts appliance usage via the Behavioral Segmentation Agent.
- It communicates with the Facilitating Agent to notify other system components of demand response actions.

Inputs:
- Grid connection: Simulated or actual grid connection for receiving demand response requests.
- Prediction Agent: Provides predicted energy demand data.
- Behavioral Segmentation Agent: Adjusts appliance usage to reduce energy consumption.
- Facilitating Agent: Coordinates and notifies other agents about system-wide actions.

Outputs:
- Executes curtailment actions to balance energy supply and demand.
- Notifies other agents about ongoing demand response activities.

Agents Needed:
1. Prediction Agent: Supplies predicted energy demand.
2. Behavioral Segmentation Agent: Manages appliance usage adjustments.
3. Facilitating Agent: Communicates and coordinates with other agents in the system.
"""

class DemandResponseAgent:
    def __init__(self, grid_connection, prediction_agent, behavioral_agent, facilitating_agent):
        """
        Initializes the Demand Response Agent with required connections and agents.

        Args:
        grid_connection (str): Connection to the energy grid (simulated or real).
        prediction_agent (PredictionAgent): Instance of the Prediction Agent.
        behavioral_agent (BehavioralSegmentationAgent): Instance of the Behavioral Segmentation Agent.
        facilitating_agent (FacilitatingAgent): Instance of the Facilitating Agent.
        """
        self.grid_connection = grid_connection
        self.prediction_agent = prediction_agent
        self.behavioral_agent = behavioral_agent
        self.facilitating_agent = facilitating_agent

    def receive_demand_response_request(self):
        """
        Receives demand response requests from the grid.

        Returns:
        bool: True if a demand response event is requested, False otherwise.
        """
        demand_response_event = True  # Placeholder for actual grid communication logic
        return demand_response_event

    def plan_curtailment(self):
        """
        Plans curtailment actions based on predicted energy demand.

        Uses:
        - Prediction Agent: To get the predicted demand.
        - Behavioral Segmentation Agent: To adjust appliance usage.
        - Facilitating Agent: To notify other agents.

        No direct output but triggers appliance adjustments and notifications.
        """
        predicted_demand = self.prediction_agent.get_predicted_demand()
        if predicted_demand > 80:  # Example threshold
            print(f"High demand predicted: {predicted_demand}")
            self.behavioral_agent.adjust_appliance_usage()
            self.facilitating_agent.notify_other_agents("Curtailment action initiated.")
        else:
            print(f"Demand is normal: {predicted_demand}")

    def execute_curtailment(self):
        """
        Executes curtailment actions when a demand response request is received.

        Checks for demand response requests and triggers curtailment planning if necessary.
        """
        curtailment_required = self.receive_demand_response_request()
        if curtailment_required:
            print("Demand response activated. Initiating curtailment.")
            self.plan_curtailment()
        else:
            print("No demand response required at this time.")

    def run(self):
        """
        Continuously runs the Demand Response Agent to monitor and act on demand response requests.

        This is a blocking method that periodically checks for demand response requests and manages curtailment.
        """
        import time
        while True:
            time.sleep(5)  # Periodic check
            self.execute_curtailment()

# Mock Prediction Agent
class PredictionAgent:
    def get_predicted_demand(self):
        """
        Simulates retrieving predicted energy demand.

        Returns:
        int: Simulated predicted demand value.
        """
        import random
        return random.randint(70, 100)  # Simulated demand

# Mock Behavioral Segmentation Agent
class BehavioralSegmentationAgent:
    def adjust_appliance_usage(self):
        """
        Simulates adjusting appliance usage to meet curtailment goals.

        No return value, prints adjustment actions.
        """
        print("Adjusting appliance usage based on curtailment plan.")

# Mock Facilitating Agent
class FacilitatingAgent:
    def notify_other_agents(self, message):
        """
        Simulates notifying other agents about system-wide actions.

        Args:
        message (str): The message to send to other agents.
        """
        print(f"Notifying other agents: {message}")

# Example usage
grid_connection = "Simulated Grid Connection"  # Placeholder for grid connection
prediction_agent = PredictionAgent()
behavioral_agent = BehavioralSegmentationAgent()
facilitating_agent = FacilitatingAgent()

# Instantiate and run the Demand Response Agent
demand_response_agent = DemandResponseAgent(grid_connection, prediction_agent, behavioral_agent, facilitating_agent)
demand_response_agent.run()
