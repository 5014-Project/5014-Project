# system_simulator.py

"""
Module: System Simulator for Energy Management System

Description:
    This module simulates the performance of the entire energy management system under different scenarios.
    It can simulate varying levels of energy demand, supply, grid conditions, and agent interactions to
    evaluate how the system responds.

Inputs:
    - Scenarios (e.g., varying demand, appliance usage, energy prices)
    - System parameters (e.g., number of agents, energy production capacity)

Outputs:
    - Simulation results (e.g., energy consumption, grid stability, agent performance)

Agents Needed:
    - PredictionAgent: To provide demand forecasts
    - DemandResponseAgent: To implement demand response strategies
    - BehavioralSegmentationAgent: To predict and adjust appliance usage
    - NegotiationAgent: To simulate market bidding and energy trading
    - FacilitatingAgent: To facilitate communication between agents
"""

import random
from agents.prediction_agent import PredictionAgent
from agents.demand_response_agent import DemandResponseAgent
from agents.behavioral_agent import BehavioralSegmentationAgent
from agents.negotiation_agent import NegotiationAgent
from agents.facilitating_agent import FacilitatingAgent

class SystemSimulator:
    def __init__(self, agents, scenarios):
        """
        Initializes the system simulator.

        :param agents: List of agents that participate in the system (e.g., prediction, demand response, etc.)
        :param scenarios: List of different scenarios to test (e.g., varying energy demand)
        """
        self.agents = agents
        self.scenarios = scenarios
        self.results = []

    def simulate_scenario(self, scenario):
        """
        Simulates system performance for a given scenario.

        :param scenario: The scenario to be simulated (e.g., increased demand, low supply)
        :return: Simulation results for the scenario
        """
        print(f"Simulating scenario: {scenario['name']}")

        energy_demand = scenario['demand'] + random.uniform(-5, 5)
        energy_supply = scenario['supply'] + random.uniform(-3, 3)

        if energy_demand > energy_supply:
            self.agents['demand_response_agent'].send_demand_response(energy_demand)
            result = "Demand response activated."
        else:
            result = "System is stable."

        self.results.append({
            'scenario': scenario['name'],
            'energy_demand': energy_demand,
            'energy_supply': energy_supply,
            'result': result
        })

    def run_simulation(self):
        """
        Runs the entire simulation for all provided scenarios.
        """
        for scenario in self.scenarios:
            self.simulate_scenario(scenario)

    def get_results(self):
        """
        Returns the results of the simulations.
        """
        return self.results


# Example Usage
if __name__ == "__main__":
    agents = {
        'demand_response_agent': DemandResponseAgent(),
        'prediction_agent': PredictionAgent(),
        'behavioral_agent': BehavioralSegmentationAgent(),
        'negotiation_agent': NegotiationAgent(),
        'facilitating_agent': FacilitatingAgent()
    }

    scenarios = [
        {'name': 'High Demand', 'demand': 100, 'supply': 80},
        {'name': 'Low Supply', 'demand': 90, 'supply': 70},
        {'name': 'Normal Conditions', 'demand': 80, 'supply': 80}
    ]

    simulator = SystemSimulator(agents, scenarios)
    simulator.run_simulation()
    print(simulator.get_results())
