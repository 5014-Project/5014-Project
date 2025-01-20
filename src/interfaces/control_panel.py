# control_panel.py

"""
Module: Control Panel for Managing Energy Settings

Description:
    This module allows users to control and adjust energy-related settings such as appliance priority,
    demand response thresholds, and trading behavior. The panel interacts with the back-end system to
    implement user-defined changes.

Inputs:
    - User input from control interface (e.g., changing thresholds or priorities)

Outputs:
    - Confirmation of settings adjustment and system updates

Agents Needed:
    - BehavioralSegmentationAgent: To adjust appliance usage and priorities
    - DemandResponseAgent: To modify demand response thresholds
"""

from tkinter import Tk, Button, Label, Scale
from agents.behavioral_agent import BehavioralSegmentationAgent
from agents.demand_response_agent import DemandResponseAgent

class ControlPanel:
    def __init__(self, behavioral_agent: BehavioralSegmentationAgent, demand_response_agent: DemandResponseAgent):
        """
        Initializes the control panel.

        :param behavioral_agent: Instance of the BehavioralSegmentationAgent to adjust appliance behavior
        :param demand_response_agent: Instance of the DemandResponseAgent to adjust demand response thresholds
        """
        self.behavioral_agent = behavioral_agent
        self.demand_response_agent = demand_response_agent
        self.window = Tk()
        self.window.title("Control Panel")

        # Create UI components
        self.label = Label(self.window, text="Control Panel for Energy Settings", font=("Arial", 16))
        self.label.pack()

        self.priority_slider = Scale(self.window, from_=1, to=5, orient="horizontal", label="Priority Level")
        self.priority_slider.pack()

        self.threshold_slider = Scale(self.window, from_=50, to=100, orient="horizontal", label="Demand Threshold")
        self.threshold_slider.pack()

        self.apply_button = Button(self.window, text="Apply Settings", command=self.apply_settings)
        self.apply_button.pack()

    def apply_settings(self):
        """
        Apply the new settings based on user input from the control panel.
        """
        priority_level = self.priority_slider.get()
        demand_threshold = self.threshold_slider.get()

        # Update agents based on the user input
        self.behavioral_agent.adjust_appliance_usage(priority_level)
        self.demand_response_agent.set_demand_threshold(demand_threshold)

        self.label.config(text=f"Settings Applied: Priority {priority_level}, Threshold {demand_threshold}%")

    def run(self):
        """
        Runs the control panel UI.
        """
        self.window.mainloop()


# Example Usage
if __name__ == "__main__":
    behavioral_agent = BehavioralSegmentationAgent()
    demand_response_agent = DemandResponseAgent()

    control_panel = ControlPanel(behavioral_agent, demand_response_agent)
    control_panel.run()
