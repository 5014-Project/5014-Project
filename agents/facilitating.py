import json
from datetime import datetime
import asyncio
import time
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

# Define the FacilitatingAgent class as before
class FacilitatingAgent(Agent):
    class MultiAgentHandler(CyclicBehaviour):
        async def on_start(self):
            self.dependencies = {
                "gui": ["house", "negotiation", "behavioralsegmentation"],
                "prediction": ["house"],
                "demandresponse": ["grid", "house"],
                "negotiation": ["house", "prediction", "demandresponse", "gui"],
                "behavioralsegmentation": ["house", "demandresponse"],
                "grid" : [],
                "house" : []
            }
            self.last_message = {agent: {"time": datetime.now(), "msg": None} for agent in self.dependencies}
            self.startup = True

        async def run(self):
            log_prefix = "[FacilitatingAgent]"

            def time_from_now(message_timing):
                # Handle initial min time case
                if message_timing["time"] == datetime.min: return float('inf')
                return (datetime.now() - message_timing["time"]).total_seconds()

            # --- Receive Message ---
            msg = await self.receive(timeout=5) # Shorter timeout for more responsiveness

            if msg:
                sender_jid = str(msg.sender).lower()
                agent_name = sender_jid.split('@')[0]

                # --- Conditional Logging ---
                # Define agents whose message bodies should NOT be fully logged
                suppress_body_log_for = ["grid", "demandresponse"] # Add demandresponse here

                if agent_name in suppress_body_log_for:
                    print(f"{log_prefix} Received message from {sender_jid} (Body not logged)")
                else:
                    # Log body for other agents if reasonably short
                    try:
                         body_str = str(msg.body) # Get body as string
                         if len(body_str) < 300: # Shorter limit?
                              print(f"{log_prefix} Received message from {sender_jid}: {body_str}")
                         else:
                              print(f"{log_prefix} Received message from {sender_jid} (Body length: {len(body_str)})")
                    except Exception as e_log:
                         print(f"{log_prefix} Error preparing message body for logging from {sender_jid}: {e_log}")
                # --- End Conditional Logging ---


                # --- Store Message ---
                if agent_name in self.last_message:
                    try:
                        # Attempt to parse JSON, store raw on failure
                        parsed_body = json.loads(msg.body)
                        self.last_message[agent_name]["msg"] = parsed_body
                    except json.JSONDecodeError:
                         print(f"{log_prefix} Warning: Non-JSON message from {sender_jid}. Storing raw.")
                         self.last_message[agent_name]["msg"] = msg.body # Store raw string
                    except Exception as e_parse:
                         print(f"{log_prefix} Error parsing/storing message from {sender_jid}: {e_parse}")
                         self.last_message[agent_name]["msg"] = None # Store None on other errors
                    finally:
                         # Update timestamp even if parsing failed
                         self.last_message[agent_name]["time"] = datetime.now()
                else:
                    print(f"{log_prefix} Received message from unrecognized agent: {sender_jid}")


            # --- Dependency Resolution and Sending ---
            dependency_check_interval = 5 # Check dependencies every X seconds approx
            now_time = time.time()
            if not hasattr(self, 'last_dependency_check') or (now_time - self.last_dependency_check > dependency_check_interval):
                self.last_dependency_check = now_time
                # print(f"{log_prefix} Checking dependencies...") # Reduce noise

                for agent_target in self.dependencies:
                    # Skip agents with no dependencies
                    if not self.dependencies[agent_target]:
                        # print(f"{log_prefix} {agent_target} has no dependencies.") # Reduce noise
                        continue

                    unresolved_dependencies = []
                    dict_to_send = {}
                    can_resolve = True
                    max_dependency_age = 30 # How old can data be? (seconds)

                    # Check each dependency for the target agent
                    for dependency_name in self.dependencies[agent_target]:
                        if dependency_name not in self.last_message:
                             print(f"{log_prefix} ERROR: Dependency '{dependency_name}' needed by '{agent_target}' is not defined in self.last_message!")
                             can_resolve = False
                             break # Cannot resolve if dependency definition missing

                        dep_data = self.last_message[dependency_name]
                        if dep_data["msg"] is None or time_from_now(dep_data) > max_dependency_age:
                            unresolved_dependencies.append(dependency_name)
                            can_resolve = False
                        else:
                            dict_to_send[dependency_name] = dep_data["msg"]

                    # If all dependencies are met, send the aggregated message
                    if can_resolve:
                        agent_address = f"{agent_target}@localhost"
                        try:
                            json_dump = json.dumps(dict_to_send)
                            response = Message(to=agent_address, body=json_dump)
                            await self.send(response)
                            # print(f"{log_prefix} Sent resolved dependencies to {agent_target}") # Reduce noise
                        except TypeError as te:
                             print(f"{log_prefix} ERROR: JSON serialization failed for {agent_target}. TypeErr: {te}")
                             # Log structure for debugging?
                             # print(f"   Data causing error: {dict_to_send}")
                        except Exception as e_send:
                             print(f"{log_prefix} ERROR sending message to {agent_target}: {e_send}")
                    # else: # Only log if there were unresolved ones
                    #     if unresolved_dependencies:
                    #          print(f"{log_prefix} Awaiting {unresolved_dependencies} for agent {agent_target}")


            # Sleep at the end of the main loop
            await asyncio.sleep(1) # Loop approx once per second


        async def setup(self):
            print("[FacilitatingAgent] Started")
            handler = self.MultiAgentHandler()
            self.add_behaviour(handler)
            # Initialize last check time for dependency sending
            self.last_dependency_check = time.time() - 10 # Check soon after start