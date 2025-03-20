from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import time
import asyncio

# Negotiation Agent: Facilitates peer-to-peer energy trading
class House(Agent):
    class HouseStatus(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(5)
            print("[House] Sending current consumption and production data...")
            msg = await self.receive(timeout=5)
            response = Message(to="facilitating@localhost")
            response.body = json.dumps({
                "current_demand": 100,
                "current_production": 100,
                "appliances":[{
                        "item": "Blender",
                        "priority": 1
                    },
                    {
                        "item": "Game System",
                        "priority": 1
                    },
                    {
                        "item": "TV",
                        "priority": 1
                    },
                    {
                        "item": "Heater",
                        "priority": 4
                    },
                    {
                        "item": "Washing Machine",
                        "priority": 3
                    }]
                })
            await self.send(response)
            print(f"[House] Sent current data to FacilitatingAgent: {response.body}")

    
    async def setup(self):
        print("[House] Started")
        self.add_behaviour(self.HouseStatus())
        self.web.start(hostname="localhost", port="9091")