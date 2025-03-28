# File: agents/prediction.py

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import time
import asyncio
import os
import tensorflow as tf
import numpy as np
import sqlite3 # Import sqlite3

# --- Database Configuration ---
DB_NAME = "energy_data.db"

# --- Helper Functions ---
def initialize_predictions_table(db_name):
    """Creates the predictions table if it doesn't exist."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,          -- Unix timestamp when prediction was made
                predicted_demand REAL,   -- Forecasted demand value (local home)
                predicted_production REAL -- Forecasted production value (local home)
            )
        """)
        conn.commit()
        conn.close()
        print("[PredictionAgent] Predictions table checked/created.")
    except sqlite3.Error as sql_err:
        print(f"[PredictionAgent] ERROR initializing predictions table (sqlite3): {sql_err}")
    except Exception as e:
         print(f"[PredictionAgent] ERROR initializing predictions table (generic): {e}")

def log_prediction(db_name, timestamp, demand, production):
    """Logs local prediction data to the database."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (timestamp, predicted_demand, predicted_production)
            VALUES (?, ?, ?)
        """, (timestamp, float(demand), float(production))) # Ensure values are float
        conn.commit()
        conn.close()
    except sqlite3.Error as sql_err:
        print(f"[PredictionAgent] ERROR logging prediction (sqlite3): {sql_err}")
    except Exception as e:
        print(f"[PredictionAgent] ERROR logging prediction (generic): {e}")


# --- Prediction Agent Definition ---
class PredictionAgent(Agent):
    """Forecasts local energy demand and production based on input data."""

    class PredictBehaviour(CyclicBehaviour):
        async def on_start(self):
            """Loads the LSTM model when the behaviour starts."""
            self.model = None # Initialize model state
            print("[PredictionAgent] Behaviour starting, loading model...")
            try:
                # Use absolute path for reliability
                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                model_path = os.path.join(project_dir, "models", "energy_lstm.keras")

                if not os.path.exists(model_path):
                     print(f"[PredictionAgent] FATAL ERROR: Model file not found at {model_path}")
                     # Stop the behaviour or agent if model is critical
                     self.kill(exit_code=1) # Stop the behaviour
                     return

                self.model = tf.keras.models.load_model(model_path)
                print("[PredictionAgent] LSTM Model loaded successfully.")
            except Exception as e:
                 print(f"[PredictionAgent] FATAL ERROR loading LSTM model: {e}")
                 self.kill(exit_code=1) # Stop behaviour if model load fails

        async def run(self):
            """
            Cyclic loop: Wait for data, predict, log, send message.
            """
            # Check if model loaded correctly in on_start
            if self.model is None:
                 print("[PredictionAgent] Model not loaded, cannot predict. Stopping behaviour.")
                 self.kill(exit_code=1)
                 return

            # print("[PredictionAgent] Waiting for house input data...") # Reduce noise
            msg = await self.receive(timeout=15) # Wait for message

            if msg:
                sender_jid = str(msg.sender).lower()
                # print(f"[PredictionAgent] Received message from {sender_jid}") # Reduce noise
                if "house@" not in sender_jid: # Basic check for expected sender
                     # print("[PredictionAgent] Ignoring message from unexpected sender.")
                     await asyncio.sleep(1) # Short sleep if ignoring
                     return

                try:
                    # Expect structure: {"house": {"test_sample": [...]}}
                    data = json.loads(msg.body)
                    house_data = data.get("house", {})
                    raw_test_sample = house_data.get("test_sample")

                    if not raw_test_sample:
                        print("[PredictionAgent] No 'test_sample' data found in message.")
                        return # Skip cycle

                    # --- Data Validation and Processing ---
                    extracted_data = []
                    # Expect sample like [[[v1],[v2],...]]
                    if isinstance(raw_test_sample, list) and raw_test_sample and isinstance(raw_test_sample[0], list):
                         # Flatten and validate items
                         extracted_data = [item[0] for item in raw_test_sample[0] if isinstance(item, list) and len(item) > 0 and isinstance(item[0], (int, float))]
                    else:
                         print("[PredictionAgent] 'test_sample' format invalid (expected list of lists).")

                    # Ensure correct length and type after extraction
                    expected_length = 18 # Or whatever your model requires
                    if len(extracted_data) != expected_length:
                        print(f"[PredictionAgent] Invalid data length ({len(extracted_data)} != {expected_length}). Skipping.")
                        return

                    # Convert and reshape for the LSTM model
                    test_sample_np = np.array(extracted_data).astype(np.float32)
                    # Reshape to (batch_size, timesteps, features) -> (1, 18, 1)
                    test_sample_input = test_sample_np.reshape(1, expected_length, 1)

                    # --- Make Prediction ---
                    prediction_result = self.model.predict(test_sample_input)
                    # Assuming model output shape is (1, 2) -> [[demand, production]]
                    predicted_demand = prediction_result[0][0]
                    predicted_production = prediction_result[0][1]
                    # print(f"[PredictionAgent] Prediction: Demand={predicted_demand:.4f}, Prod={predicted_production:.4f}") # Reduce noise

                    # --- Log Prediction to Database ---
                    current_timestamp = time.time()
                    log_prediction(DB_NAME, current_timestamp, predicted_demand, predicted_production)
                    # print("[PredictionAgent] Prediction logged to database.") # Reduce noise

                    # --- Send Prediction Message (to FacilitatingAgent) ---
                    response_msg = Message(to="facilitating@localhost")
                    response_msg.body = json.dumps({
                        "predicted_demand": float(predicted_demand),
                        "predicted_production": float(predicted_production)
                    })
                    await self.send(response_msg)
                    # print(f"[PredictionAgent] Sent prediction to Facilitator.") # Reduce noise

                except json.JSONDecodeError as e:
                    print(f"[PredictionAgent] JSON decode error: {e}")
                except ValueError as ve:
                    print(f"[PredictionAgent] Data processing/reshape error: {ve}")
                    print(f"   Problematic raw_test_sample: {str(raw_test_sample)[:100]}...") # Log snippet
                except Exception as e:
                    print(f"[PredictionAgent] ERROR in run loop: {e}")
                    import traceback
                    traceback.print_exc() # Show full trace for unexpected errors

            # else: print("[PredictionAgent] No message received.") # Reduce noise

            # Short sleep before next cycle starts
            await asyncio.sleep(5) # Adjust loop frequency as needed

    async def setup(self):
        """Initializes the agent, database table, behaviour, and web server."""
        print(f"[PredictionAgent] {self.jid} starting setup...")
        # Initialize DB Table
        initialize_predictions_table(DB_NAME)
        # Add prediction behaviour
        predict_b = self.PredictBehaviour()
        self.add_behaviour(predict_b)
        print("[PredictionAgent] Predict behaviour added.")
        # Start web server (if needed for this agent specifically)
        try:
            # Note: This agent doesn't currently seem to need a web server based on logic
            # If it does, uncomment and configure:
            # await self.web.start(hostname="localhost", port=9096)
            # print("[PredictionAgent] Web server started on port 9096.")
            pass # Remove if web server not needed
        except Exception as e:
            print(f"[PredictionAgent] Failed to start web server (if configured): {e}")
        print(f"[PredictionAgent] {self.jid} setup complete.")