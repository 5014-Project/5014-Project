"""
FacilitatingAgent.py

This file contains the implementation of the Facilitating Agent for the Smart Home Energy Management System.
The agent acts as a coordinator and interface, facilitating communication between all other agents in the system and managing the overall workflow.

Usage:
- This agent serves as the communication hub, relaying messages and data between the Prediction Agent, Demand Response Agent, Behavioral Segmentation Agent, Negotiation Agent, and the user interface.

Inputs:
- Messages and data from other agents.
- User commands and preferences.

Outputs:
- Coordinated actions and responses based on inputs from various agents.
- Notifications and updates to the user interface.

Agents Needed:
1. Prediction Agent: For energy production and consumption forecasts.
2. Demand Response Agent: For handling demand response events and curtailment instructions.
3. Behavioral Segmentation Agent: For optimizing appliance usage.
4. Negotiation Agent: For managing peer-to-peer energy trading.
"""

class FacilitatingAgent:
    def __init__(self):
        """
        Initializes the Facilitating Agent with references to other agents in the system.
        """
        self.prediction_agent = None
        self.demand_response_agent = None
        self.behavioral_agent = None
        self.negotiation_agent = None

    def register_agents(self, prediction_agent, demand_response_agent, behavioral_agent, negotiation_agent):
        """
        Registers the other agents with the Facilitating Agent.

        Args:
        prediction_agent (PredictionAgent): Instance of the Prediction Agent.
        demand_response_agent (DemandResponseAgent): Instance of the Demand Response Agent.
        behavioral_agent (BehavioralSegmentationAgent): Instance of the Behavioral Segmentation Agent.
        negotiation_agent (NegotiationAgent): Instance of the Negotiation Agent.
        """
        self.prediction_agent = prediction_agent
        self.demand_response_agent = demand_response_agent
        self.behavioral_agent = behavioral_agent
        self.negotiation_agent = negotiation_agent
        print("Agents registered successfully.")

    def relay_message(self, sender, recipient, message):
        """
        Relays a message from one agent to another.

        Args:
        sender (str): The name of the sending agent.
        recipient (str): The name of the receiving agent.
        message (str): The message content.
        """
        print(f"Relaying message from {sender} to {recipient}: {message}")
        if recipient == "PredictionAgent" and self.prediction_agent:
            self.prediction_agent.receive_message(message)
        elif recipient == "DemandResponseAgent" and self.demand_response_agent:
            self.demand_response_agent.receive_message(message)
        elif recipient == "BehavioralSegmentationAgent" and self.behavioral_agent:
            self.behavioral_agent.receive_message(message)
        elif recipient == "NegotiationAgent" and self.negotiation_agent:
            self.negotiation_agent.receive_message(message)
        else:
            print(f"Unknown recipient or agent not registered: {recipient}")

    def notify_other_agents(self, message):
        """
        Notifies all other agents about a system-wide event.

        Args:
        message (str): The message to send to all agents.
        """
        print(f"Broadcasting message to all agents: {message}")
        if self.prediction_agent:
            self.prediction_agent.receive_message(message)
        if self.demand_response_agent:
            self.demand_response_agent.receive_message(message)
        if self.behavioral_agent:
            self.behavioral_agent.receive_message(message)
        if self.negotiation_agent:
            self.negotiation_agent.receive_message(message)

# Example implementation of an agent receiving a message
class ExampleAgent:
    def receive_message(self, message):
        """
        Simulates receiving a message from the Facilitating Agent.

        Args:
        message (str): The message content.
        """
        print(f"ExampleAgent received message: {message}")

# Example usage
facilitating_agent = FacilitatingAgent()

# Mock agents for demonstration
prediction_agent = ExampleAgent()
demand_response_agent = ExampleAgent()
behavioral_agent = ExampleAgent()
negotiation_agent = ExampleAgent()

# Registering mock agents
facilitating_agent.register_agents(prediction_agent, demand_response_agent, behavioral_agent, negotiation_agent)

# Relaying a message
facilitating_agent.relay_message("DemandResponseAgent", "BehavioralSegmentationAgent", "Curtailment plan received.")
