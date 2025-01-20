{
    "system_settings": {
        "system_name": "Smart Home Energy Management",
        "location": "Ontario, Canada",  // Location for climate and energy consumption data
        "time_zone": "America/Toronto",  // Time zone of the system
        "simulation_mode": true,  // Whether to run the system in simulation mode
        "real_time_monitoring": true,  // Whether to enable real-time monitoring
        "communication_protocol": "MQTT",  // Communication protocol for agent interactions
        "data_logging": {
            "enable_logging": true,  // Whether to enable system data logging
            "log_file": "system_data.log",  // File to store system logs
            "max_log_size_mb": 100  // Maximum size of log file before rotation
        }
    },
    "energy_management": {
        "energy_source": "solar",  // Primary energy source (solar, grid, etc.)
        "battery_storage": {
            "enabled": true,  // Whether battery storage is available
            "capacity_kWh": 10,  // Battery capacity in kWh
            "charging_rate": 2,  // Rate of charging (kWh per hour)
            "discharging_rate": 2  // Rate of discharging (kWh per hour)
        },
        "peak_demand_threshold": 80,  // Threshold (in %) above which demand response is triggered
        "demand_response": {
            "enabled": true,  // Enable demand response
            "response_time": 15,  // Time to respond to a demand request (minutes)
            "penalty": 0.05  // Penalty for non-compliance with demand response
        }
    },
    "agent_configuration": {
        "prediction_agent": {
            "model_file": "lstm_model.pkl",  // Path to the trained LSTM model file
            "prediction_horizon": 24  // Number of hours to predict ahead
        },
        "behavioral_agent": {
            "data_file": "appliance_data.csv",  // Path to the appliance data
            "segmentation_method": "kmeans",  // Segmentation method (e.g., kmeans)
            "num_clusters": 3  // Number of clusters for appliance behavior
        },
        "negotiation_agent": {
            "auction_model_file": "auction_model.pkl",  // Path to the auction model
            "max_bids": 5  // Maximum number of bids per auction
        }
    },
    "testing": {
        "enable_unit_tests": true,  // Whether to enable unit tests for system components
        "test_log_file": "test_results.log"  // File to store test results
    }
}
