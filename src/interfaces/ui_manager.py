# ui_manager.py

"""
Module: User Interface Manager for Energy Management System

Description:
    This module handles interactions with the user interface, including initializing the UI components
    and managing user inputs and outputs. It integrates with the system’s components to display data,
    collect user input, and send requests to the back-end system.

Inputs:
    - User input via graphical user interface (e.g., control settings, simulation start)
    
Outputs:
    - Display system status, performance metrics, and control options

Agents Needed:
    - FacilitatingAgent: To communicate user requests to back-end agents and retrieve results
"""

from tkinter import Tk, Button, Label
from agents.facilitating_agent import FacilitatingAgent

class UIManager:
    def __init__(self, facilitating_agent: FacilitatingAgent):
        """
        Initializes the UI Manager.

        :param facilitating_agent: Instance of the FacilitatingAgent to handle communication with system components
        """
        self.facilitating_agent = facilitating_agent
        self.window = Tk()
        self.window.title("Energy Management System UI")

        # Create UI components
        self.label = Label(self.window, text="Energy Management System", font=("Arial", 20))
        self.label.pack()

        self.start_button = Button(self.window, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack()

        self.control_button = Button(self.window, text="Control Settings", command=self.control_settings)
        self.control_button.pack()

    def start_simulation(self):
        """
        Starts the energy management system simulation by invoking the facilitating agent.
        """
        result = self.facilitating_agent.start_simulation()
        self.label.config(text=f"Simulation Started: {result}")

    def control_settings(self):
        """
        Opens the control panel for managing energy-related settings.
        """
        # This could open a new window for controlling energy consumption
        self.label.config(text="Control Panel Opened")

    def run(self):
        """
        Runs the UI window, allowing user interaction.
        """
        self.window.mainloop()


# Example Usage
if __name__ == "__main__":
    facilitating_agent = FacilitatingAgent()
    ui_manager = UIManager(facilitating_agent)
    ui_manager.run()
