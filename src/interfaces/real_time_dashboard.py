# real_time_dashboard.py

"""
Module: Real-Time Dashboard for Energy Usage and Trading Status

Description:
    This module visualizes real-time data about the system’s energy usage, appliance consumption, and
    trading status. It provides a graphical dashboard that updates frequently to give the user an overview
    of the energy system’s state.

Inputs:
    - Real-time data from agents (e.g., energy consumption, trading status)

Outputs:
    - Real-time visualizations of energy usage and trading status

Agents Needed:
    - PredictionAgent: To display predicted energy demand
    - BehavioralSegmentationAgent: To visualize appliance usage patterns
    - NegotiationAgent: To display the status of energy trading
"""

import matplotlib.pyplot as plt
from agents.prediction_agent import PredictionAgent
from agents.behavioral_agent import BehavioralSegmentationAgent
from agents.negotiation_agent import NegotiationAgent
from matplotlib.animation import FuncAnimation

class RealTimeDashboard:
    def __init__(self, prediction_agent: PredictionAgent, behavioral_agent: BehavioralSegmentationAgent, negotiation_agent: NegotiationAgent):
        """
        Initializes the real-time dashboard.

        :param prediction_agent: Instance of the PredictionAgent for predicted energy demand data
        :param behavioral_agent: Instance of the BehavioralSegmentationAgent for appliance usage data
        :param negotiation_agent: Instance of the NegotiationAgent for energy trading status
        """
        self.prediction_agent = prediction_agent
        self.behavioral_agent = behavioral_agent
        self.negotiation_agent = negotiation_agent

        # Initialize plot for real-time dashboard
        self.fig, self.ax = plt.subplots()
        self.time = []
        self.energy_usage = []
        self.trading_status = []

    def update_dashboard(self, frame):
        """
        Updates the dashboard with new data for each frame.

        :param frame: Frame number for animation
        """
        predicted_demand = self.prediction_agent.get_predicted_demand()
        appliance_data = self.behavioral_agent.appliance_data['Energy_Consumption'].sum()
        trading_status = self.negotiation_agent.get_trading_status()

        self.time.append(frame)
        self.energy_usage.append(appliance_data)
        self.trading_status.append(trading_status)

        self.ax.clear()
        self.ax.plot(self.time, self.energy_usage, label="Energy Usage")
        self.ax.plot(self.time, self.trading_status, label="Trading Status", linestyle="--")

        self.ax.set_title("Real-Time Energy Management Dashboard")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Energy (kWh)")
        self.ax.legend()

    def run(self):
        """
        Starts the dashboard animation.
        """
        ani = FuncAnimation(self.fig, self.update_dashboard, interval=1000)
        plt.show()


# Example Usage
if __name__ == "__main__":
    prediction_agent = PredictionAgent()
    behavioral_agent = BehavioralSegmentationAgent()
    negotiation_agent = NegotiationAgent()

    dashboard = RealTimeDashboard(prediction_agent, behavioral_agent, negotiation_agent)
    dashboard.run()
