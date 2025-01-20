"""
system_manager.py

This file contains the logic for managing the entire Smart Home Energy Management System.
It coordinates the actions of all agents and ensures that energy management is optimized.
It handles data flow, agent interaction, and decision-making processes.

Usage:
- Initializes and coordinates agents for prediction, demand response, behavior segmentation, and facilitating energy trading.
- Acts as the central hub that manages the overall functioning of the smart home energy system.

Inputs:
- Raw energy data (appliance, renewable, grid data).
- Predictions from the PredictionAgent.
- Demand response requests and adjustments.

Outputs:
- Actions triggered by agents (e.g., adjustments in appliance usage, demand response initiation).
- Status reports on system performance.

Agents:
- BehavioralSegmentationAgent
- PredictionAgent
- DemandResponseAgent
- FacilitatingAgent
"""

from behavioral_agent import BehavioralSegmentationAgent
from prediction_agent import PredictionAgent
from demand_response_agent import DemandResponseAgent
from facilitating_agent import FacilitatingAgent
from energy_data_processor import EnergyDataProcessor

class SystemManager:
    """
    The SystemManager coordinates the interaction of different agents in the Smart Home Energy Management System.
    It ensures that energy consumption and production are optimized and balanced across the system.
    """

    def __init__(self, appliance_data, renewable_data, grid_data):
        """
        Initializes the system manager with necessary energy data and agent instances.
        
        :param appliance_data: Raw energy consumption data from appliances.
        :param renewable_data: Raw renewable energy production data.
        :param grid_data: Raw grid energy consumption data.
        """
        # Initialize agents
        self.prediction_agent = PredictionAgent()
        self.demand_response_agent = DemandResponseAgent()
        self.facilitating_agent = FacilitatingAgent()

        # Initialize data processor
        self.energy_data_processor = EnergyDataProcessor(appliance_data, renewable_data, grid_data)
        
        # Initialize Behavioral Segmentation Agent
        self.behavioral_segmentation_agent = BehavioralSegmentationAgent(
            appliance_data, self.prediction_agent, self.demand_response_agent, self.facilitating_agent
        )

    def process_data(self):
        """
        Process energy data and prepare it for use by other agents.
        - Cleans, aggregates, and scales energy data.
        """
        appliance_data_scaled, renewable_data_scaled, grid_data_scaled = self.energy_data_processor.process_all_data()
        return appliance_data_scaled, renewable_data_scaled, grid_data_scaled

    def manage_energy(self):
        """
        Manages energy usage by coordinating the actions of all agents.
        - Adjusts appliance usage, initiates demand response, and updates system status.
        """
        # Step 1: Process data
        appliance_data_scaled, renewable_data_scaled, grid_data_scaled = self.process_data()

        # Step 2: Behavioral segmentation and appliance usage adjustment
        high_priority, medium_priority, low_priority = self.behavioral_segmentation_agent.run()

        # Step 3: Predict future energy demand and decide on demand response actions
        predicted_demand = self.prediction_agent.get_predicted_demand()

        # If predicted demand is high, trigger demand response
        if predicted_demand > 80:  # Threshold for initiating demand response
            self.demand_response_agent.send_demand_response(predicted_demand)
            self.facilitating_agent.notify_other_agents("Demand response activated. Adjusting appliance usage.")
        
        # Step 4: Monitor system status
        self.monitor_system()

    def monitor_system(self):
        """
        Monitors the status of the system and logs any important information or issues.
        """
        print("System monitoring:")
        # Here we can log the current status of energy usage, production, and demand
        # E.g., print current appliance usage, renewable energy production, etc.
        print("System is running smoothly.")

# Example usage
if __name__ == "__main__":
    # Simulate energy data (replace with actual data)
    appliance_data = pd.DataFrame({
        'timestamp': pd.date_range(start="2025-01-01", periods=24, freq='H'),
        'Energy_Consumption': np.random.rand(24)
    })
    
    renewable_data = pd.DataFrame({
        'timestamp': pd.date_range(start="2025-01-01", periods=24, freq='H'),
        'Energy_Production': np.random.rand(24)
    })
    
    grid_data = pd.DataFrame({
        'timestamp': pd.date_range(start="2025-01-01", periods=24, freq='H'),
        'Energy_Consumption': np.random.rand(24)
    })
    
    # Initialize the system manager
    system_manager = SystemManager(appliance_data, renewable_data, grid_data)
    
    # Run the energy management process
    system_manager.manage_energy()
