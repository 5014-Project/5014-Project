# evaluation_metrics.py

"""
Module: System Performance Evaluation Metrics

Description:
    This module evaluates the performance of the energy management system based on various metrics such as
    energy efficiency, cost savings, grid stability, and the effectiveness of demand response strategies.

Inputs:
    - System data (e.g., energy consumption, cost, grid stability)
    - Simulation results (from `system_simulator.py`)

Outputs:
    - Performance scores and evaluations (e.g., energy savings, grid stability)

Agents Needed:
    - FacilitatingAgent: To facilitate the evaluation of system-wide performance
"""

import numpy as np

class EvaluationMetrics:
    def __init__(self, simulation_results):
        """
        Initializes the evaluation metrics evaluator.

        :param simulation_results: List of results from system simulations
        """
        self.simulation_results = simulation_results

    def calculate_energy_efficiency(self):
        """
        Calculates the energy efficiency based on simulation data.
        Energy efficiency could be defined as the ratio of energy used efficiently to total energy demand.
        """
        total_energy_demand = sum(result['energy_demand'] for result in self.simulation_results)
        total_energy_used = sum(result['energy_supply'] for result in self.simulation_results)
        energy_efficiency = total_energy_used / total_energy_demand

        return energy_efficiency

    def calculate_cost_savings(self, energy_price_per_kWh=0.15):
        """
        Calculates the cost savings based on reduced energy usage or improved efficiency.
        """
        total_energy_used = sum(result['energy_supply'] for result in self.simulation_results)
        cost_savings = total_energy_used * energy_price_per_kWh

        return cost_savings

    def calculate_grid_stability(self):
        """
        Evaluates the system's grid stability based on how often demand exceeds supply.
        A higher frequency of imbalance may indicate lower stability.
        """
        imbalance_count = sum(1 for result in self.simulation_results if result['energy_demand'] > result['energy_supply'])
        grid_stability = 1 - (imbalance_count / len(self.simulation_results))  # Higher stability = closer to 1

        return grid_stability

    def evaluate_performance(self):
        """
        Evaluates system performance by calculating various metrics.
        """
        energy_efficiency = self.calculate_energy_efficiency()
        cost_savings = self.calculate_cost_savings()
        grid_stability = self.calculate_grid_stability()

        return {
            'Energy Efficiency': energy_efficiency,
            'Cost Savings ($)': cost_savings,
            'Grid Stability': grid_stability
        }


# Example Usage
if __name__ == "__main__":
    simulation_results = [
        {'scenario': 'High Demand', 'energy_demand': 100, 'energy_supply': 80, 'result': 'Demand response activated.'},
        {'scenario': 'Low Supply', 'energy_demand': 90, 'energy_supply': 70, 'result': 'Demand response activated.'},
        {'scenario': 'Normal Conditions', 'energy_demand': 80, 'energy_supply': 80, 'result': 'System is stable.'}
    ]

    evaluator = EvaluationMetrics(simulation_results)
    performance_metrics = evaluator.evaluate_performance()

    print(performance_metrics)
