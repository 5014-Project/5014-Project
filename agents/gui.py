# File: agents/gui.py

# --- Imports ---
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import sqlite3
import time
import asyncio
from aiohttp import web # For web server request/response handling

# --- Configuration ---
DB_NAME = "energy_data.db"
GUI_AGENT_WEB_PORT = 9099 # Port for Streamlit to send strategy updates to

# --- GUIAgent Class Definition ---
class GUIAgent(Agent):
    """
    This agent acts as an interface between the Streamlit GUI and the MAS.
    - It receives actual energy production/consumption data (e.g., from a House agent)
      and logs it to the database for the dashboard.
    - It maintains the current trading strategy selected via the Streamlit GUI.
    - It runs a web server endpoint (/set_strategy) allowing Streamlit to update the strategy.
    - It periodically sends the current strategy to the FacilitatingAgent.
    """
    def __init__(self, jid, password, *args, **kwargs):
        """Initializes the agent with default strategy and DB status."""
        super().__init__(jid, password, *args, **kwargs)
        self.db_name = DB_NAME
        self.current_strategy = "neutral" # Default strategy on startup
        self.db_initialized = False
        print(f"[GUIAgent] Initialized. Default strategy: '{self.current_strategy}'. Waiting for setup...")

    def initialize_database(self):
        """Creates tables for storing actual energy data if they do not exist."""
        if self.db_initialized:
            # print("[GUIAgent] Database already initialized.") # Reduce noise
            return
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            # Tables managed by this agent
            tables = {
                "energy_production": "CREATE TABLE IF NOT EXISTS energy_production (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, value REAL)",
                "energy_consumption": "CREATE TABLE IF NOT EXISTS energy_consumption (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, value REAL)"
            }
            print(f"[GUIAgent] Connecting to DB '{self.db_name}' and initializing tables...")
            for name, query in tables.items():
                cursor.execute(query)
            conn.commit()
            conn.close()
            self.db_initialized = True
            print("[GUIAgent] Database tables (energy_production, energy_consumption) checked/created.")
        except sqlite3.Error as sql_err:
            print(f"[GUIAgent] CRITICAL sqlite3 ERROR initializing database tables: {sql_err}")
        except Exception as e:
            print(f"[GUIAgent] CRITICAL generic ERROR initializing database tables: {e}")

    def store_data(self, table, value):
        """Inserts actual energy data (production/consumption) into the DB."""
        if not self.db_initialized:
            print("[GUIAgent] Warning: DB not initialized. Attempting init before storing.")
            self.initialize_database()
            if not self.db_initialized: # If init failed again
                 print("[GUIAgent] ERROR: Cannot store data, DB initialization failed.")
                 return

        # Validate input value
        if value is None or not isinstance(value, (int, float)):
             # print(f"[GUIAgent] Warning: Invalid value type '{type(value)}' for table '{table}', skipping store.") # Reduce noise
             return

        try:
            timestamp = time.time()
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table} (timestamp, value) VALUES (?, ?)", (timestamp, float(value)))
            conn.commit()
            conn.close()
        except sqlite3.Error as sql_err:
            print(f"[GUIAgent] ERROR storing data to {table} (sqlite3 error): {sql_err}")
        except Exception as e:
             print(f"[GUIAgent] ERROR storing data to {table} (generic error): {e}")

    # --- Web Controller Inner Class ---
    # Handles HTTP requests made to this agent's web server
    class GUIAgentWebController:
        def __init__(self, agent_instance):
            """Stores a reference to the parent GUIAgent."""
            self.agent = agent_instance

        async def set_strategy(self, request: web.Request):
            """
            Handles POST requests to /set_strategy endpoint.
            Expects JSON body: {"strategy": "new_strategy_value"}
            Updates the agent's internal state.
            """
            print("[GUIAgent][Web] Received request on /set_strategy")
            if not request.body_exists or not request.can_read_body:
                print("[GUIAgent][Web] /set_strategy Error: Request body required.")
                return web.json_response({"status": "error", "message": "Request body required"}, status=400)

            try:
                data = await request.json()
                new_strategy = data.get("strategy")
                valid_strategies = ["aggressive", "neutral", "conservative"]

                # Validate the received strategy
                if new_strategy and isinstance(new_strategy, str) and new_strategy in valid_strategies:
                    # --- Update Agent State ---
                    self.agent.current_strategy = new_strategy
                    # --- Log the change ---
                    print(f"[GUIAgent][Web] Strategy successfully updated to: '{self.agent.current_strategy}'")
                    # --- Send success response ---
                    return web.json_response({"status": "ok", "message": f"Strategy set to {new_strategy}"}, status=200)
                else:
                    # Log invalid input and send error response
                    invalid_value = str(new_strategy)[:50] # Limit length for logging
                    print(f"[GUIAgent][Web] /set_strategy Error: Invalid strategy value received: '{invalid_value}'")
                    return web.json_response({"status": "error", "message": f"Invalid or missing strategy field. Must be one of {valid_strategies}."}, status=400)

            except json.JSONDecodeError:
                 # Handle cases where request body is not valid JSON
                 print("[GUIAgent][Web] /set_strategy Error: Invalid JSON format received.")
                 return web.json_response({"status": "error", "message": "Invalid JSON format"}, status=400)
            except Exception as e:
                 # Catch unexpected errors during processing
                 print(f"[GUIAgent][Web] /set_strategy Error: Internal error processing request: {e}")
                 return web.json_response({"status": "error", "message": "Internal server error"}, status=500)

    # --- Main SPADE Behaviour Inner Class ---
    # Runs continuously to handle messages and periodic tasks
    class guiBehaviour(CyclicBehaviour):
        async def run(self):
            """
            Cyclic loop:
            1. Check for incoming messages (e.g., house data) and log them.
            2. Send the current strategy to the FacilitatingAgent.
            3. Sleep.
            """
            # 1. Receive House Data & Store Actuals (non-blocking check)
            try:
                msg = await self.receive(timeout=0.5) # Very short timeout, don't block long
                if msg:
                    sender_jid = str(msg.sender).lower()
                    # Only process messages expected to contain house data
                    if "house@" in sender_jid:
                        try:
                            data = json.loads(msg.body)
                            house_data = data.get("house") # Expect data under 'house' key
                            if house_data and isinstance(house_data, dict):
                                # Extract specific keys if structure is known
                                prod = house_data.get("current_production")
                                cons = house_data.get("current_demand")
                                # Log if values are present
                                if prod is not None: self.agent.store_data("energy_production", prod)
                                if cons is not None: self.agent.store_data("energy_consumption", cons)
                            # else: print(f"[GUIAgent] Message from {sender_jid} lacked 'house' dict.") # Reduce noise
                        except json.JSONDecodeError:
                            print(f"[GUIAgent] JSON decode error processing message from {sender_jid}.")
                        except Exception as e_proc:
                            print(f"[GUIAgent] Error processing message from {sender_jid}: {e_proc}")
                    # else: print(f"[GUIAgent] Ignored message from {sender_jid}") # Reduce noise
            except Exception as e_recv:
                print(f"[GUIAgent] Error during message receive: {e_recv}")


            # 2. Send Current Strategy to Facilitator (Periodic)
            try:
                strategy_to_send = self.agent.current_strategy # Get current state
                response = Message(to="facilitating@localhost")
                response.body = json.dumps({"strategy": strategy_to_send})
                await self.send(response)
                # print(f"[GUIAgent] Sent strategy '{strategy_to_send}' to Facilitator.") # Reduce noise
            except Exception as e_send:
                 print(f"[GUIAgent] Error sending strategy message: {e_send}")

            # 3. Control loop speed
            await asyncio.sleep(5) # Interval for sending strategy updates

    # --- Agent Setup Method ---
    async def setup(self):
        """
        Sets up the agent's behaviours and web server upon starting.
        """
        print(f"[GUIAgent] {self.jid} starting setup...")
        self.initialize_database() # Ensure DB tables are checked/created

        # Add main cyclic behaviour
        main_b = self.guiBehaviour()
        self.add_behaviour(main_b)
        print("[GUIAgent] Main behaviour added.")

        # Setup and Start Web Server for strategy updates
        try:
            print(f"[GUIAgent] Setting up web server on port {GUI_AGENT_WEB_PORT}...")
            # Create instance of the web controller, passing the agent instance
            controller = self.GUIAgentWebController(self)

            # Define an async function to add routes to the app router
            # This function will be called by SPADE's web server during startup
            async def setup_routes(app):
                app.router.add_post("/set_strategy", controller.set_strategy)
                print("[GUIAgent] Web route POST /set_strategy added.")

            # Register the route setup function with the SPADE web service
            self.web.add_routes_setup(setup_routes)

            # Start the SPADE web server (which runs aiohttp internally)
            await self.web.start(hostname="localhost", port=GUI_AGENT_WEB_PORT)
            print(f"[GUIAgent] Web server started successfully at http://localhost:{GUI_AGENT_WEB_PORT}")

        except AttributeError:
             # Fallback for older SPADE versions that might not have add_routes_setup
             print("[GUIAgent] Web setup warning: 'add_routes_setup' method not found. Trying fallback...")
             try:
                  # Start first, then try adding route (less standard, might have issues)
                  await self.web.start(hostname="localhost", port=GUI_AGENT_WEB_PORT)
                  if hasattr(self.web, "app") and hasattr(self.web.app, "router"):
                       controller = self.GUIAgentWebController(self) # Need controller here too
                       self.web.app.router.add_post("/set_strategy", controller.set_strategy)
                       print(f"[GUIAgent] Web server started (fallback route add successful).")
                  else:
                       print("[GUIAgent] Fallback failed: Could not access web app router after start.")
                       raise RuntimeError("Web app router not accessible for fallback.")
             except Exception as fallback_e:
                  print(f"[GUIAgent] CRITICAL ERROR starting web server (fallback attempt): {fallback_e}")
                  print("[GUIAgent] Strategy control via GUI will NOT work.")

        except Exception as e:
            # Catch any other errors during standard web server startup
            print(f"[GUIAgent] CRITICAL ERROR starting web server: {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging
            print("[GUIAgent] Strategy control via GUI will NOT work.")

        print(f"[GUIAgent] {self.jid} setup complete.")

