from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import random
import os
import numpy as np
import tensorflow as tf
import json
import time

# Prediction Agent: Forecasts energy demand and production
class PredictionAgent(Agent):
    class PredictBehaviour(CyclicBehaviour):
        async def on_start(self):
            self.model_path = os.path.join("models", "energy_lstm.keras")
            self.model = tf.keras.models.load_model(self.model_path)

        async def run(self):
            time.sleep(1)
            print("[PredictionAgent] Waiting for input data...")
            msg = await self.receive(timeout=5)
            if msg:
                try:
                    X_test = np.string2array(msg.body) 
                    #print(f"[PredictionAgent] Received data: {X_test}")

                    #ordered by demand, production of house.
                    test_sample = X_test.reshape(1, X_test.shape, 1)  # Reshape for LSTM input
                    
                    # Make Prediction
                    prediction = self.model.predict(test_sample)
                    print(f"🔹 test set Sample Prediction:")
                    print(f"   - Energy Usage: {prediction[0][0]:.2f} kWh")
                    print(f"   - Solar Generation: {prediction[0][1]:.2f} kWh")
                   
                    response = Message(to="facilitating@localhost")
                    response.body = json.dumps({
                        "predicted_demand": float(prediction[0][0]),
                        "predicted_production": float(prediction[0][1])
                    })
                    await self.send(response)
                    print(f"[PredictionAgent] Sent prediction data to FacilitatingAgent...")
                except json.JSONDecodeError:
                    print(f"[PredictionAgent] Invalid message format: {msg.body}")
            time.sleep(1)
    
    async def setup(self):
        print("[PredictionAgent] Started")
        self.add_behaviour(self.PredictBehaviour())
        self.web.start(hostname="localhost", port="9096")