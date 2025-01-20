"""
energy_data_processor.py

This file contains the logic for processing energy consumption and production data.
It includes functions for acquiring, cleaning, transforming, and integrating energy data from various sources,
such as appliances, renewable energy systems (solar/wind), and the energy grid.

Usage:
- Collects and processes energy data to make it usable for prediction, segmentation, demand response, and trading agents.
- Provides cleaned, transformed, and feature-engineered data to other agents.

Inputs:
- Raw energy data (e.g., appliance-level consumption, solar/wind production, grid data).
- Time-series data such as hourly or daily energy consumption and production.

Outputs:
- Processed and feature-engineered energy data for use in other components of the system.

Agents:
- BehavioralSegmentationAgent
- PredictionAgent
- DemandResponseAgent
- FacilitatingAgent
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class EnergyDataProcessor:
    """
    Processes energy data for use by various agents in the Smart Home Energy Management System.
    This includes collecting, cleaning, transforming, and feature engineering the data.
    """

    def __init__(self, appliance_data, renewable_data, grid_data):
        """
        Initializes the EnergyDataProcessor with different data sources.
        
        :param appliance_data: DataFrame containing appliance-level energy consumption data.
        :param renewable_data: DataFrame containing renewable energy production data (e.g., solar, wind).
        :param grid_data: DataFrame containing grid energy consumption data.
        """
        self.appliance_data = appliance_data
        self.renewable_data = renewable_data
        self.grid_data = grid_data
        self.scaler = StandardScaler()  # For normalizing data
        
    def clean_data(self):
        """
        Cleans and preprocesses raw energy data.
        - Handle missing values
        - Remove outliers
        - Normalize or scale data
        
        Returns:
        - Cleaned and preprocessed appliance, renewable, and grid data
        """
        # Example cleaning - handle missing values and outliers (basic)
        self.appliance_data.fillna(self.appliance_data.mean(), inplace=True)  # Fill missing with mean
        self.renewable_data.fillna(self.renewable_data.mean(), inplace=True)
        self.grid_data.fillna(self.grid_data.mean(), inplace=True)
        
        # Remove outliers (basic example: values outside 3 standard deviations)
        self.appliance_data = self.appliance_data[(np.abs(self.appliance_data - self.appliance_data.mean()) <= (3 * self.appliance_data.std()))]
        self.renewable_data = self.renewable_data[(np.abs(self.renewable_data - self.renewable_data.mean()) <= (3 * self.renewable_data.std()))]
        self.grid_data = self.grid_data[(np.abs(self.grid_data - self.grid_data.mean()) <= (3 * self.grid_data.std()))]

        return self.appliance_data, self.renewable_data, self.grid_data

    def aggregate_data(self, data, time_freq='H'):
        """
        Aggregates data to a specific time frequency (e.g., hourly, daily).
        
        :param data: Raw energy data.
        :param time_freq: Desired frequency for aggregation ('H' for hourly, 'D' for daily).
        
        Returns:
        - Aggregated energy data
        """
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data_resampled = data.resample(time_freq, on='timestamp').sum()  # Sum energy over the specified frequency
        return data_resampled

    def feature_engineering(self):
        """
        Performs feature engineering on energy data.
        - Create additional time-based features (e.g., time of day, day of week)
        - Calculate rolling averages or energy usage patterns
        
        Returns:
        - Feature-engineered data for use by agents
        """
        # Example: Create time-based features
        self.appliance_data['hour'] = self.appliance_data['timestamp'].dt.hour
        self.renewable_data['hour'] = self.renewable_data['timestamp'].dt.hour
        self.grid_data['hour'] = self.grid_data['timestamp'].dt.hour

        # Example: Calculate rolling mean for appliances over 3 hours (this helps to smooth out fluctuations)
        self.appliance_data['rolling_mean'] = self.appliance_data['Energy_Consumption'].rolling(window=3).mean()

        return self.appliance_data, self.renewable_data, self.grid_data

    def scale_data(self):
        """
        Scales energy data (appliance, renewable, and grid data) for modeling purposes.
        
        Returns:
        - Scaled appliance, renewable, and grid data
        """
        self.appliance_data[['Energy_Consumption']] = self.scaler.fit_transform(self.appliance_data[['Energy_Consumption']])
        self.renewable_data[['Energy_Production']] = self.scaler.fit_transform(self.renewable_data[['Energy_Production']])
        self.grid_data[['Energy_Consumption']] = self.scaler.fit_transform(self.grid_data[['Energy_Consumption']])

        return self.appliance_data, self.renewable_data, self.grid_data

    def process_all_data(self):
        """
        Processes all raw energy data: cleans, aggregates, engineers features, and scales.
        
        Returns:
        - Fully processed and scaled data ready for use by agents.
        """
        appliance_data_clean, renewable_data_clean, grid_data_clean = self.clean_data()
        appliance_data_aggregated = self.aggregate_data(appliance_data_clean)
        renewable_data_aggregated = self.aggregate_data(renewable_data_clean)
        grid_data_aggregated = self.aggregate_data(grid_data_clean)

        appliance_data_features, renewable_data_features, grid_data_features = self.feature_engineering()
        appliance_data_scaled, renewable_data_scaled, grid_data_scaled = self.scale_data()

        return appliance_data_scaled, renewable_data_scaled, grid_data_scaled


# Example usage
if __name__ == "__main__":
    # Simulate energy data (Replace with actual data)
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
    
    processor = EnergyDataProcessor(appliance_data, renewable_data, grid_data)
    processed_data = processor.process_all_data()
    print(processed_data)
