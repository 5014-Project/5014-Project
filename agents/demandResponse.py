# File: agents/demandResponse.py

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
from datetime import datetime
import time
import asyncio
import os
import tensorflow as tf
import numpy as np
import sqlite3 # Import sqlite3
import joblib # Import joblib for scalers

# --- Database Configuration ---
DB_NAME = "energy_data.db" # Use the same DB name as other agents

# --- Helper Functions ---

def get_energy_rate(timestamp):
    """Determines the current energy rate ($/kWh) based on timestamp and predefined time-of-use schedule."""
    current_time = datetime.fromtimestamp(timestamp)
    # Define Time-of-Use periods (adjust hours/rates as needed)
    # Ultra-low rate: 11 PM (23:00) to 7 AM (06:59) everyday
    if current_time.hour >= 23 or current_time.hour < 7:
        return 0.028  # 2.8¢ per kWh
    # Weekend off-peak: 7 AM (07:00) to 11 PM (22:59) on weekends (Sat/Sun)
    elif current_time.weekday() >= 5:  # Saturday (5) or Sunday (6)
        # During the day on weekends is off-peak
        return 0.076  # 7.6¢ per kWh
    # Weekday (Mon-Fri)
    else:
        # Mid-peak: 7 AM (07:00) to 4 PM (15:59) AND 9 PM (21:00) to 11 PM (22:59)
        if (7 <= current_time.hour < 16) or (21 <= current_time.hour < 23):
            return 0.122  # 12.2¢ per kWh
        # On-peak: 4 PM (16:00) to 9 PM (20:59)
        elif 16 <= current_time.hour < 21:
            return 0.284  # 28.4¢ per kWh
        else:
             # Should not happen with current logic, but default to ultra-low if missed
             return 0.028

def initialize_dr_table(db_name):
    """Creates the demand response log table if it doesn't exist."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demand_response_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,               -- Unix timestamp of calculation
                grid_predicted_demand REAL,   -- Grid-level demand forecast (UNSCALED units, e.g., MW)
                grid_predicted_supply REAL,   -- Grid-level supply forecast (UNSCALED units, e.g., MW)
                energy_rate_per_kwh REAL,    -- Calculated energy rate ($/kWh)
                curtailment_kw REAL          -- Calculated curtailment signal (kW or MW, match prediction units)
            )
        """)
        conn.commit()
        conn.close()
        print("[DemandResponseAgent] Demand Response log table checked/created.")
    except sqlite3.Error as sql_err:
        print(f"[DemandResponseAgent] ERROR initializing DR table (sqlite3): {sql_err}")
    except Exception as e:
        print(f"[DemandResponseAgent] ERROR initializing DR table (generic): {e}")

def log_demand_response(db_name, timestamp, grid_demand, grid_supply, rate, curtailment):
    """Logs demand response related data (predictions, rate, curtailment) to the database."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO demand_response_log
                (timestamp, grid_predicted_demand, grid_predicted_supply, energy_rate_per_kwh, curtailment_kw)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, float(grid_demand), float(grid_supply), float(rate), float(curtailment)))
        conn.commit()
        conn.close()
    except sqlite3.Error as sql_err:
        print(f"[DemandResponseAgent] ERROR logging DR data (sqlite3): {sql_err}")
    except Exception as e:
        print(f"[DemandResponseAgent] ERROR logging DR data (generic): {e}")


# --- Demand Response Agent Definition ---
class DemandResponseAgent(Agent):
    """
    Predicts overall grid demand and supply using dedicated models.
    Calculates the current energy rate based on time-of-use.
    Determines a potential curtailment signal based on predicted grid deficit.
    Logs this information to the database for the dashboard.
    Sends this information to the FacilitatingAgent.
    """

    class DRBehaviour(CyclicBehaviour):
        """The main behaviour handling prediction, calculation, logging, and messaging."""

        async def on_start(self):
            """Load prediction models and scalers when the behaviour starts."""
            self.model_demand = None
            self.model_supply = None
            self.demand_scaler = None
            self.supply_scaler = None
            print("[DemandResponseAgent][Behavior] Starting setup: Loading models and scalers...")

            try:
                # Determine project directory dynamically
                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

                # Define paths (ensure these filenames match your saved files)
                model_path_demand = os.path.join(project_dir, "models", "lstm_cnn_demand_predictor.keras")
                model_path_supply = os.path.join(project_dir, "models", "lstm_cnn_supply_predictor.keras")
                scaler_path_demand = os.path.join(project_dir, "models", "grid_demand_scaler.joblib")
                scaler_path_supply = os.path.join(project_dir, "models", "grid_supply_scaler.joblib")

                model_loaded = True
                scaler_loaded = True

                # Load Demand Model
                if os.path.exists(model_path_demand):
                    self.model_demand = tf.keras.models.load_model(model_path_demand)
                    print("[DR][Behavior] Grid Demand Predictor Model loaded.")
                else:
                    print(f"[DR][Behavior] ERROR: Demand model not found: {model_path_demand}")
                    model_loaded = False

                # Load Supply Model
                if os.path.exists(model_path_supply):
                    self.model_supply = tf.keras.models.load_model(model_path_supply)
                    print("[DR][Behavior] Grid Supply Predictor Model loaded.")
                else:
                    print(f"[DR][Behavior] ERROR: Supply model not found: {model_path_supply}")
                    model_loaded = False

                # Load Demand Scaler
                if os.path.exists(scaler_path_demand):
                    self.demand_scaler = joblib.load(scaler_path_demand)
                    print("[DR][Behavior] Grid Demand Scaler loaded.")
                else:
                    print(f"[DR][Behavior] ERROR: Demand scaler not found: {scaler_path_demand}")
                    scaler_loaded = False

                # Load Supply Scaler
                if os.path.exists(scaler_path_supply):
                    self.supply_scaler = joblib.load(scaler_path_supply)
                    print("[DR][Behavior] Grid Supply Scaler loaded.")
                else:
                    print(f"[DR][Behavior] ERROR: Supply scaler not found: {scaler_path_supply}")
                    scaler_loaded = False

                # Stop behaviour if critical components are missing
                if not model_loaded or not scaler_loaded:
                     print("[DR][Behavior] FATAL ERROR: One or more models/scalers failed to load. Stopping behaviour.")
                     self.kill(exit_code=1) # Stop this specific behaviour instance

            except ImportError:
                 print("[DR][Behavior] FATAL ERROR: 'joblib' not installed. Please run 'pip install joblib'. Stopping behaviour.")
                 self.kill(exit_code=1)
            except Exception as e:
                 print(f"[DemandResponseAgent][Behavior] FATAL ERROR during on_start loading: {e}")
                 import traceback
                 traceback.print_exc()
                 self.kill(exit_code=1) # Stop behaviour on any critical load error

        async def run(self):
            """Cyclic execution: wait for message, predict, calculate, log, send."""

            # Check if setup (on_start) completed successfully
            # Added check for self being set, might fail very early if kill() was called in on_start
            if not hasattr(self, 'model_demand') or not hasattr(self, 'model_supply') or \
               not hasattr(self, 'demand_scaler') or not hasattr(self, 'supply_scaler') or \
               not all([self.model_demand, self.model_supply, self.demand_scaler, self.supply_scaler]):
                 # This check might not be strictly necessary if self.kill was effective, but added defensively
                 print("[DR][Behavior] Models/Scalers not loaded (setup failed?). Skipping cycle.")
                 await asyncio.sleep(30) # Wait longer before retrying or stopping
                 # Consider stopping permanently: self.kill(exit_code=1)
                 return

            # print("[DR] Waiting for grid data...") # Reduce noise
            msg = await self.receive(timeout=15) # Wait for a message containing grid data

            if msg:
                sender_jid = str(msg.sender).lower()
                # print(f"[DR] Received message from {sender_jid}") # Reduce noise

                # --- Process only expected messages ---
                if "grid@" not in sender_jid:
                    # print(f"[DR] Ignoring message from unexpected sender: {sender_jid}")
                    await asyncio.sleep(1) # Small delay if ignoring
                    return

                try:
                    # --- Parse and Validate Input Data ---
                    # Expecting format: {"grid": {"test_sample_supply": [...], "test_sample_demand": [...]}}
                    grid_data = json.loads(msg.body).get("grid")
                    if not grid_data or not isinstance(grid_data, dict) or \
                       "test_sample_supply" not in grid_data or "test_sample_demand" not in grid_data:
                        print("[DR] Message received, but 'grid' data format is incomplete or missing.")
                        return # Skip cycle if data structure is wrong

                    # --- Prepare Data for Models ---
                    # This part is highly dependent on how your models were trained
                    # and the format of data sent by the Grid agent.
                    # Using the placeholder logic assuming [[v1],[v2]...] format for now.
                    # !!! THIS NEEDS TO BE VERIFIED/ADJUSTED !!!
                    try:
                        raw_demand = grid_data["test_sample_demand"]
                        raw_supply = grid_data["test_sample_supply"]
                        expected_length = 18 # Example, adjust to your model's timestep requirement

                        if isinstance(raw_demand, list) and raw_demand and isinstance(raw_demand[0], list):
                             demand_flat = [item[0] for item in raw_demand[0] if isinstance(item, list) and len(item)>0 and isinstance(item[0], (int, float))]
                             if len(demand_flat) == expected_length:
                                 # Reshape to (batch_size=1, timesteps=18, features=1)
                                 test_sample_demand = np.array(demand_flat).astype(np.float32).reshape(1, expected_length, 1)
                             else: raise ValueError(f"Demand data length {len(demand_flat)} != {expected_length}")
                        else: raise ValueError("Demand data format unexpected (expected list of lists)")

                        if isinstance(raw_supply, list) and raw_supply and isinstance(raw_supply[0], list):
                             supply_flat = [item[0] for item in raw_supply[0] if isinstance(item, list) and len(item)>0 and isinstance(item[0], (int, float))]
                             if len(supply_flat) == expected_length:
                                 # Reshape to (batch_size=1, timesteps=18, features=1)
                                 test_sample_supply = np.array(supply_flat).astype(np.float32).reshape(1, expected_length, 1)
                             else: raise ValueError(f"Supply data length {len(supply_flat)} != {expected_length}")
                        else: raise ValueError("Supply data format unexpected (expected list of lists)")

                    except (ValueError, TypeError, IndexError) as data_e:
                         print(f"[DR] Error processing/validating input samples: {data_e}")
                         print(f"   Raw Demand Snippet: {str(raw_demand)[:100]}...")
                         print(f"   Raw Supply Snippet: {str(raw_supply)[:100]}...")
                         return # Skip cycle if data preparation fails

                    # --- Make Scaled Predictions ---
                    predicted_demand_scaled = self.model_demand.predict(test_sample_demand)[0][0]
                    predicted_supply_scaled = self.model_supply.predict(test_sample_supply)[0][0]

                    # --- Inverse Transform using Loaded Scalers ---
                    try:
                         # Scalers expect 2D array [[value]] for single feature inverse transform
                         grid_predicted_demand = self.demand_scaler.inverse_transform([[predicted_demand_scaled]])[0][0]
                         grid_predicted_supply = self.supply_scaler.inverse_transform([[predicted_supply_scaled]])[0][0]
                    except Exception as scale_e:
                         print(f"[DR] ERROR during inverse transform: {scale_e}. Cannot proceed.")
                         return # Fail cycle if scaling doesn't work

                    # --- Calculate Rate and Curtailment ---
                    current_timestamp = time.time()
                    energy_rate = get_energy_rate(current_timestamp) # $/kWh
                    market_value = energy_rate # Assuming market value for trading is current TOU rate

                    curtailment_kw = 0.0 # Default: No curtailment needed
                    predicted_deficit = grid_predicted_demand - grid_predicted_supply
                    if predicted_deficit > 0:
                        # Apply curtailment logic (e.g., 10% of predicted grid deficit)
                        # Ensure units are consistent (e.g., both predictions in kW or MW)
                        curtailment_kw = max(0, predicted_deficit * 0.1) # Ensure non-negative

                    # print(f"[DR] Predictions(Unscaled): D={grid_predicted_demand:.1f}, S={grid_predicted_supply:.1f} | Rate: {energy_rate:.4f}, Curtail: {curtailment_kw:.2f}") # Reduce noise

                    # --- Log Data to Database ---
                    log_demand_response(
                        DB_NAME, current_timestamp,
                        grid_predicted_demand, grid_predicted_supply,
                        energy_rate, curtailment_kw
                    )
                    # print("[DR] DR data logged to database.") # Reduce noise

                    # --- Send Calculated Data to FacilitatingAgent ---
                    response_data = {
                        # Send UNSCALED grid predictions
                        "predicted_demand": float(grid_predicted_demand),
                        "predicted_supply": float(grid_predicted_supply),
                        "market_value" : float(market_value), # Current rate
                        "curtailment": float(curtailment_kw), # Curtailment signal
                        "energy_rate": float(energy_rate),    # Current rate (same as market_value here)
                        # Recommendations are optional - include if used by other agents
                        # "recommended_appliance_behaviour": [...]
                    }
                    response_msg = Message(to="facilitating@localhost")
                    response_msg.body = json.dumps(response_data)
                    await self.send(response_msg)
                    # print(f"[DR] Sent DR data to Facilitator.") # Reduce noise

                # --- Error Handling for message processing ---
                except json.JSONDecodeError as e:
                    print(f"[DR] JSON decode error processing message from {sender_jid}: {e}")
                except ValueError as ve: # Catch data processing/validation errors
                     print(f"[DR] Data processing error: {ve}")
                except Exception as e: # Catch unexpected errors
                    print(f"[DR] UNEXPECTED ERROR in run loop processing message: {e}")
                    import traceback
                    traceback.print_exc() # Print full trace for debugging

            # else: print("[DR] No message received in timeout.") # Reduce noise

            # Pause before next loop cycle
            await asyncio.sleep(5) # Adjust frequency of checking for messages/running DR logic

    async def setup(self):
        """Initializes the agent: database table, behaviour, web server (optional)."""
        print(f"[DemandResponseAgent] {self.jid} starting setup...")
        # Ensure DB table exists
        initialize_dr_table(DB_NAME)
        # Create and add the main behaviour
        dr_b = self.DRBehaviour()
        self.add_behaviour(dr_b)
        print("[DemandResponseAgent] DR behaviour added.")

        # Start web server ONLY if this agent needs to expose HTTP endpoints
        # Currently, it doesn't seem to based on the logic.
        # try:
        #     await self.web.start(hostname="localhost", port=9094)
        #     print("[DemandResponseAgent] Web server started on port 9094.")
        # except Exception as e:
        #     print(f"[DemandResponseAgent] Failed to start web server (if configured): {e}")

        print(f"[DemandResponseAgent] {self.jid} setup complete.")

