from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import os   
import numpy as np
import json
import time

# Negotiation Agent: Facilitates peer-to-peer energy trading
class House(Agent):
    class HouseStatus(CyclicBehaviour):
        async def on_start(self):
            self.idx = 0
            self.data_path = os.path.join("test_agents", "energy_test_set.npz")
            self.data = np.load(self.data_path)

        async def run(self):
            print("[House] Sending current consumption and production data...")
            msg = await self.receive(timeout=5)
            response = Message(to="facilitating@localhost")
            response.body = np.array2string(self.data["X_test"][self.idx])
            self.idx = (self.idx + 1) % (len(self.data["X_test"])-1)
            await self.send(response)
            print(f"[House] Sent current data to FacilitatingAgent...")

    async def setup(self):
        print("[House] Started")
        self.add_behaviour(self.HouseStatus())
        self.web.start(hostname="localhost", port="9091")