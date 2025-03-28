from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from web3 import Web3
import json
import os
from dotenv import load_dotenv
import asyncio
import time
import sqlite3
from datetime import datetime, timedelta

# --- Database Configuration ---
DB_NAME = "energy_data.db"
SUMMARY_LOG_INTERVAL = 45 # Log summary every 60 seconds

# --- Constants ---
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# --- Helper Functions ---

def log_blockchain_event(db_name, timestamp, agent_account, event_type, energy_kwh, price_eth, balance_eth, counterparty=None, status="Success", auction_id=None):
    """Logs detailed blockchain events to the database."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blockchain_log (timestamp, agent_account, event_type, energy_kwh, price_eth, balance_eth, counterparty_address, status, auction_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, agent_account, event_type, energy_kwh, price_eth, balance_eth, counterparty, status, auction_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[NegotiationAgent] ERROR logging Blockchain Event: {e}")

def initialize_blockchain_table(db_name):
    """Creates the blockchain log table if it doesn't exist."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL, agent_account TEXT, event_type TEXT,
                energy_kwh REAL, price_eth REAL, balance_eth REAL,
                counterparty_address TEXT, status TEXT, auction_id INTEGER
            )
        """)
        conn.commit()
        conn.close()
        print("[NegotiationAgent] Blockchain log table initialized.")
    except Exception as e:
        print(f"[NegotiationAgent] ERROR initializing Blockchain log table: {e}")

def initialize_trade_summary_table(db_name):
    """Creates the trade summary table if it doesn't exist."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL, total_energy_bought_kwh REAL, total_energy_sold_kwh REAL
            )
        """)
        conn.commit()
        conn.close()
        print("[NegotiationAgent] Trade Summary table initialized.")
    except Exception as e:
        print(f"[NegotiationAgent] ERROR initializing Trade Summary table: {e}")

def log_trade_summary(db_name, timestamp, total_bought, total_sold):
    """Logs the cumulative trade summary to the database."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trade_summary (timestamp, total_energy_bought_kwh, total_energy_sold_kwh)
            VALUES (?, ?, ?)
        """, (timestamp, float(total_bought), float(total_sold)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[NegotiationAgent] ERROR logging Trade Summary: {e}")

# --- Negotiation Agent Definition ---
class NegotiationAgent(Agent):

    def __init__(self, jid, password, *args, **kwargs):
        super().__init__(jid, password, *args, **kwargs)
        self.total_energy_bought = 0.0
        self.total_energy_sold = 0.0
        self.db_name = DB_NAME

    class LogSummaryBehaviour(PeriodicBehaviour):
        async def run(self):
            print("[NegotiationAgent][Summary] Logging trade summary...")
            try:
                log_trade_summary(
                    self.agent.db_name, time.time(),
                    self.agent.total_energy_bought, self.agent.total_energy_sold
                )
            except Exception as e:
                print(f"[NegotiationAgent][Summary] Error during summary log: {e}")

    class TradingBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("[NegotiationAgent] Trading Behaviour starting setup...")
            # Initialize DB Tables
            initialize_blockchain_table(self.agent.db_name)
            initialize_trade_summary_table(self.agent.db_name)

            # Setup Web3 and Contract Connection
            try:
                self.web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
                if not self.web3.is_connected(): raise ConnectionError("Failed to connect to blockchain")
                print(f"[N] Ganache connected: {self.web3.is_connected()}")

                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                env_path = os.path.join(project_dir, "blockchain", ".env")
                if not load_dotenv(dotenv_path=env_path): print(f"[N] WARNING: .env not found at {env_path}")

                contract_address = os.getenv("CONTRACT_ADDRESS")
                if not contract_address: raise ValueError(".env: CONTRACT_ADDRESS not found")
                print(f"[N] Contract Address from .env: {contract_address}")

                code = self.web3.eth.get_code(contract_address)
                if code == b'0x' or code == b'': raise ValueError(f"No contract code at {contract_address}")

                contract_path = os.path.join(project_dir, "blockchain", "build", "contracts", "EnergyVickreyAuction.json")
                if not os.path.exists(contract_path): raise FileNotFoundError(f"ABI file not found: {contract_path}")
                with open(contract_path, "r") as f: contract_data = json.load(f)
                if 'abi' not in contract_data: raise ValueError("ABI missing in contract JSON")
                contract_abi = contract_data['abi']

                self.auction_contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)
                print("[N] Contract object initialized.")

                self.accounts = self.web3.eth.accounts
                if not self.accounts: raise ValueError("No accounts found in Ganache")
                self.account = self.accounts[0]
                print(f"[N] Using account: {self.account}")

                self.bid_amount = 0 # Wei
                self.nonce = "mainhouse_" + str(self.agent.jid).split('@')[0] # Slightly unique nonce

                await self.log_current_balance("Init")
                print("[NegotiationAgent] Trading Behaviour setup complete.")

            except Exception as e:
                 print(f"[NegotiationAgent] CRITICAL ERROR during on_start setup: {e}")
                 await self.agent.stop()

        async def log_current_balance(self, event_suffix="Update"):
            try:
                balance_wei = self.web3.eth.get_balance(self.account)
                balance_eth = self.web3.from_wei(balance_wei, "ether")
                log_blockchain_event(
                    db_name=self.agent.db_name, timestamp=time.time(), agent_account=self.account,
                    event_type=f"Balance {event_suffix}", energy_kwh=None, price_eth=None,
                    balance_eth=float(balance_eth), status="Success"
                )
            except Exception as e:
                print(f"[N] Failed log balance: {e}")
                try:
                    log_blockchain_event(self.agent.db_name, time.time(), self.account, f"Balance {event_suffix}", None, None, None, status="Failed")
                except Exception: pass

        def set_bid_amount(self, price_wei): self.bid_amount = price_wei
        async def create_sealed_bid(self, value_wei, nonce): return Web3.solidity_keccak(['uint256', 'string'], [value_wei, nonce])
        async def get_auction_timings(self):
            try:
                if not hasattr(self, 'auction_contract'): return 0,0,0
                bidding_start = self.auction_contract.functions.biddingStart().call()
                bidding_end = self.auction_contract.functions.biddingEnd().call()
                reveal_end = self.auction_contract.functions.revealEnd().call()
                return bidding_start, bidding_end, reveal_end
            except Exception as e: print(f"[N] Error get_auction_timings: {e}"); return 0, 0, 0
        async def wait_until(self, target_timestamp):
             if not target_timestamp or target_timestamp == 0: return
             target_dt = datetime.fromtimestamp(target_timestamp)
             wait_seconds = (target_dt - datetime.now()).total_seconds()
             if wait_seconds > 0:
                  print(f"[N] Wait {wait_seconds:.1f}s until {target_dt}")
                  await asyncio.sleep(wait_seconds + 1)

        async def start_auction(self, energy_amount_kwh):
            print(f"[N] Attempt start auction: {energy_amount_kwh:.2f} kWh")
            try:
                current_bidding_start, _, current_reveal_end = await self.get_auction_timings()
                if current_bidding_start != 0 and time.time() < current_reveal_end:
                     print("[N] Cannot start, auction in progress.")
                     return False
                contract_energy_unit = int(round(energy_amount_kwh)) # Round to nearest int kWh
                if contract_energy_unit <= 0: print("[N] Auction amount is zero or less, skipping."); return False
                tx = self.auction_contract.functions.startAuction(contract_energy_unit).transact({'from': self.account, 'gas': 3000000})
                receipt = self.web3.eth.wait_for_transaction_receipt(tx)
                print(f"[N] Auction started. Tx: ...{receipt.transactionHash.hex()[-8:]}")
                await self.log_current_balance("Post-AuctionStart")
                log_blockchain_event( self.agent.db_name, time.time(), self.account, "Auction Start", contract_energy_unit, None, float(self.web3.from_wei(self.web3.eth.get_balance(self.account), "ether")), status="Success" )
                return True
            except Exception as e:
                print(f"[N] Failed start auction: {e}")
                await self.log_current_balance("Post-AuctionStartFail")
                log_blockchain_event( self.agent.db_name, time.time(), self.account, "Auction Start", energy_amount_kwh, None, float(self.web3.from_wei(self.web3.eth.get_balance(self.account), "ether")), status="Failed" )
                return False

        async def bid(self, price_wei):
            self.set_bid_amount(price_wei)
            print(f"[N] Attempt bid {self.web3.from_wei(price_wei, 'ether'):.6f} ETH")
            try:
                sealed_bid = await self.create_sealed_bid(self.bid_amount, self.nonce)
                tx = self.auction_contract.functions.bid(sealed_bid).transact({"from": self.account, "value": self.bid_amount, "gas": 3000000})
                receipt = self.web3.eth.wait_for_transaction_receipt(tx)
                print(f"[N] Bid placed. Tx: ...{receipt.transactionHash.hex()[-8:]}")
                await self.log_current_balance("Post-Bid")
                log_blockchain_event( self.agent.db_name, time.time(), self.account, "Bid", None, float(self.web3.from_wei(self.bid_amount, "ether")), float(self.web3.from_wei(self.web3.eth.get_balance(self.account), "ether")), status="Success" )
            except Exception as e:
                print(f"[N] Failed bid: {e}")
                await self.log_current_balance("Post-BidFail")
                log_blockchain_event( self.agent.db_name, time.time(), self.account, "Bid", None, float(self.web3.from_wei(self.bid_amount, "ether")), float(self.web3.from_wei(self.web3.eth.get_balance(self.account), "ether")), status="Failed" )

        async def reveal(self):
            # Check if bid_amount is valid before attempting reveal
            if self.bid_amount <= 0:
                print("[N] Cannot reveal: No valid bid amount stored.")
                return
            print(f"[N] Attempt reveal bid: {self.web3.from_wei(self.bid_amount, 'ether'):.6f} ETH")
            try:
                tx = self.auction_contract.functions.reveal(self.bid_amount, self.nonce).transact({'from': self.account, "gas": 3000000})
                receipt = self.web3.eth.wait_for_transaction_receipt(tx)
                print(f"[N] Bid revealed. Tx: ...{receipt.transactionHash.hex()[-8:]}")
                await self.log_current_balance("Post-Reveal")
                log_blockchain_event( self.agent.db_name, time.time(), self.account, "Reveal", None, float(self.web3.from_wei(self.bid_amount, "ether")), float(self.web3.from_wei(self.web3.eth.get_balance(self.account), "ether")), status="Success" )
                # Reset bid amount after successful reveal? Optional, prevents accidental re-reveals in same phase
                # self.bid_amount = 0
            except Exception as e:
                print(f"[N] Failed reveal: {e}")
                await self.log_current_balance("Post-RevealFail")
                log_blockchain_event( self.agent.db_name, time.time(), self.account, "Reveal", None, float(self.web3.from_wei(self.bid_amount, "ether")), float(self.web3.from_wei(self.web3.eth.get_balance(self.account), "ether")), status="Failed" )

        async def closeAuction(self):
            print("[N] Attempt close auction...")
            try:
                tx = self.auction_contract.functions.closeAuction().transact({"from": self.account, "gas": 3000000})
                receipt = self.web3.eth.wait_for_transaction_receipt(tx)
                print(f"[N] Close TX successful. Tx: ...{receipt.transactionHash.hex()[-8:]}")
                await asyncio.sleep(2)

                winner = self.auction_contract.functions.highestBidder().call()
                final_price_wei = self.auction_contract.functions.secondHighestBid().call()
                final_price_eth = self.web3.from_wei(final_price_wei, "ether")
                energy_kwh = float(self.auction_contract.functions.energyAmount().call())
                contract_seller = self.auction_contract.functions.seller().call()

                print(f"[N] Closed Results: Win={winner[:10]}.., Seller={contract_seller[:10]}.., E={energy_kwh}kWh, P={final_price_eth:.6f}ETH")

                await self.log_current_balance("Post-Close")
                current_balance_eth = float(self.web3.from_wei(self.web3.eth.get_balance(self.account), "ether"))

                event_type = "Auction End (No Winner)"
                log_price = float(final_price_eth)
                log_counterparty = None

                if winner == self.account:
                    event_type = "Auction Buy"
                    self.agent.total_energy_bought += energy_kwh
                    log_counterparty = contract_seller
                    print(f"[N][Summary] Total Bought: {self.agent.total_energy_bought:.2f} kWh")
                elif winner != ZERO_ADDRESS:
                    if self.account == contract_seller:
                         event_type = "Auction Sell"
                         self.agent.total_energy_sold += energy_kwh
                         log_counterparty = winner
                         print(f"[N][Summary] Total Sold: {self.agent.total_energy_sold:.2f} kWh")
                    else:
                         event_type = "Auction End (Lost)"
                         log_counterparty = winner
                else: log_price = None

                log_blockchain_event(
                    db_name=self.agent.db_name, timestamp=time.time(), agent_account=self.account,
                    event_type=event_type, energy_kwh=energy_kwh, price_eth=log_price,
                    balance_eth=current_balance_eth, counterparty=log_counterparty, status="Success"
                )
                print(f"[N] Logged outcome: {event_type}")
                # Reset bid amount after auction closes
                self.bid_amount = 0

            except Exception as e:
                print(f"[N] Failed close/log outcome: {e}")
                import traceback; traceback.print_exc();
                await self.log_current_balance("Post-CloseFail")
                try: log_blockchain_event( self.agent.db_name, time.time(), self.account, "Auction End", None, None, float(self.web3.from_wei(self.web3.eth.get_balance(self.account), "ether")), status="Failed" )
                except Exception: pass
                # Reset bid amount even on failure?
                self.bid_amount = 0

        async def current_auction_state(self, bidding_start, bidding_end, reveal_end):
            current_time = time.time()
            state = -1
            if bidding_start == 0: state = -1
            elif current_time < bidding_start: state = 0
            elif current_time < bidding_end: state = 1 # Use < for bidding end
            elif current_time <= reveal_end: state = 2 # Use <= for reveal end
            else: state = 3
            # state_map = {-1: "No Auction", 0: "Pre-Bidding", 1:"Bidding", 2:"Reveal", 3:"Post-Reveal/Closing"}
            # print(f"[N] State: {state_map[state]} (T={datetime.now().strftime('%H:%M:%S')})")
            return state

        async def run(self):
            # ... (initial setup checks, get timings, state, close logic) ...
            if not hasattr(self, 'web3') or not self.web3.is_connected():
                 print("[N] Setup incomplete/Web3 disconnected, skipping cycle.")
                 await asyncio.sleep(10); return
            try:
                bidding_start, bidding_end, reveal_end = await self.get_auction_timings()
                current_state = await self.current_auction_state(bidding_start, bidding_end, reveal_end)

                if current_state == 3: await self.closeAuction(); await asyncio.sleep(5); return

                msg = await self.receive(timeout=10)

                if msg:
                    try: # Add try block for initial data extraction
                        data = json.loads(msg.body)
                        house_data = data.get("house") # Use get without default initially
                        # prediction_data = data.get("prediction") # Still unused
                        demand_response_data = data.get("demandresponse") # Use get without default
                        gui_data = data.get("gui") # Use get without default

                        # --- ROBUST CHECK FOR REQUIRED DATA ---
                        # Check if the core dictionaries exist and are dictionaries
                        if not isinstance(house_data, dict):
                            print(f"[N] Missing or invalid 'house' data in message.")
                            return # Skip cycle if essential data is missing/wrong type
                        if not isinstance(demand_response_data, dict):
                            print(f"[N] Missing or invalid 'demandresponse' data in message.")
                            return
                        if not isinstance(gui_data, dict):
                             print(f"[N] Missing or invalid 'gui' data in message.")
                             return
                        # Check for specific required keys WITHIN the dictionaries
                        if not all(k in house_data for k in ["current_production", "current_demand"]):
                            print(f"[N] Missing required keys in 'house' data.")
                            return
                        if "market_value" not in demand_response_data:
                             print(f"[N] Missing required 'market_value' in 'demandresponse' data.")
                             return
                        if "strategy" not in gui_data:
                              print(f"[N] Missing required 'strategy' in 'gui' data.")
                              return
                        # --- END ROBUST CHECK ---

                        # If checks pass, we can safely access the data
                        current_prod = house_data["current_production"]
                        current_demand = house_data["current_demand"]
                        market_price = demand_response_data["market_value"]
                        strategy = gui_data["strategy"]
                        energy_delta = current_prod - current_demand

                        # ... (rest of bidding/selling logic based on delta and state) ...
                        if energy_delta < -0.1: # Need to buy
                            if current_state == 1: # Bidding phase
                                # ... (bid logic) ...
                                pass
                            elif current_state == 2: # Reveal phase
                                 # ... (reveal logic) ...
                                 pass
                        elif energy_delta > 0.1: # Have surplus
                            if current_state == -1: # Only start if no auction active
                                 # ... (start auction logic) ...
                                 pass

                    except json.JSONDecodeError:
                        print(f"[N] JSON Decode Error processing received message.")
                    except Exception as e_inner: # Catch errors during data access/logic
                        print(f"[N] Error processing agent logic after receiving message: {e_inner}")
                        import traceback
                        traceback.print_exc()

                # ... (check if reveal needed without message) ...
                if current_state == 2 and self.bid_amount > 0:
                     # Check might need refinement - was reveal already attempted?
                     print("[N] State=2 (No msg check), attempting reveal...")
                     await self.reveal()

            # ... (Outer exception handling remains the same) ...
            except ConnectionError as ce: print(f"[N] Connection Error: {ce}"); await asyncio.sleep(20)
            except Exception as e: print(f"[N] Run loop ERROR: {e}"); import traceback; traceback.print_exc(); await asyncio.sleep(10)

            await asyncio.sleep(3)

    async def setup(self):
        print("[NegotiationAgent] Started")
        # Create and add behaviours
        trading_b = self.TradingBehaviour()
        self.add_behaviour(trading_b)
        start_at = datetime.now() + timedelta(seconds=15) # Delay summary log start slightly
        log_summary_b = self.LogSummaryBehaviour(period=SUMMARY_LOG_INTERVAL, start_at=start_at)
        self.add_behaviour(log_summary_b)
        print(f"[N] Summary logging added (Interval: {SUMMARY_LOG_INTERVAL}s)")

        # Start SPADE web server (if needed for other purposes, not strategy setting here)
        try:
            await self.web.start(hostname="localhost", port="9095")
            print("[N] Web server started on 9095.")
        except Exception as e:
             print(f"[N] Failed to start web server: {e}")