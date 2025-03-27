import subprocess
import time
import asyncio
import os
import signal # Keep for potential future use, though terminate/kill often sufficient
from agents.behavioralSegmentation import BehavioralSegmentationAgent
from agents.demandResponse import DemandResponseAgent
from agents.facilitating import FacilitatingAgent
from agents.negotiation import NegotiationAgent
from agents.prediction import PredictionAgent
from agents.gui import GUIAgent
from agents.grid import Grid
from agents.house import House

# --- Configuration ---
PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOCKCHAIN_DIR = os.path.join(PROJECT_ROOT_DIR, "blockchain")

# --- Process Launch Functions ---

def start_spade():
    print("🟡 Starting SPADE server (inline output)...")
    try:
        process = subprocess.Popen(["spade", "run"], shell=True) # Use shell=True for PATH
        time.sleep(2)
        exit_code = process.poll()
        if exit_code is None: print("✅ SPADE server running inline."); return process
        else: print(f"❌ SPADE server exited immediately: {exit_code}"); return None
    except Exception as e: print(f"❌ Error starting SPADE inline: {e}"); return None

def start_streamlit():
    print("🟡 Starting Streamlit UI (inline output)...")
    try:
        streamlit_file = os.path.join(PROJECT_ROOT_DIR, "streamlit_gui.py")
        process = subprocess.Popen(["streamlit", "run", streamlit_file], shell=True) # Use shell=True for PATH
        time.sleep(2)
        exit_code = process.poll()
        if exit_code is None: print("✅ Streamlit UI running inline."); return process
        else: print(f"❌ Streamlit exited immediately: {exit_code}"); return None
    except Exception as e: print(f"❌ Error starting Streamlit inline: {e}"); return None

def start_ganache():
    """Starts Ganache (v7+) in a new PowerShell window."""
    print("🟡 Starting Ganache in new PowerShell window...")
    try:
        ganache_args = "'ganache --networkId 5777 --hardfork shanghai'"
        command_list = ["powershell", "-Command", "Start-Process", "powershell", "-ArgumentList", ganache_args]
        ganache_launcher_process = subprocess.Popen(command_list)
        print("   Waiting for Ganache to initialize...")
        time.sleep(7)
        print("✅ Ganache should be running in a separate window.")
        return ganache_launcher_process
    except FileNotFoundError: print(f"❌ Error: 'powershell' not found."); return None
    except Exception as e: print(f"❌ Error starting Ganache via Start-Process: {e}"); return None

def deploy_smart_contract():
    """Deploys the smart contract using Truffle in a new PowerShell window (using Script Block)."""
    print("🟡 Deploying contract in new PowerShell window...")
    if not os.path.isdir(BLOCKCHAIN_DIR):
         print(f"❌ Error: 'blockchain' directory not found at: {BLOCKCHAIN_DIR}")
         return None

    # Use Script Block for robustness (-Command { ... })
    ps_script_block_content = f"""
        Write-Host '--- Deployment Script Started ---'
        Write-Host '   Changing directory...'
        cd '{BLOCKCHAIN_DIR}' # Use single quotes for path inside script block
        Write-Host "   New Directory: $(Get-Location)"
        Write-Host '   Setting up Node environment (fnm)...'
        fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression
        Write-Host '   Running Truffle migrate...'
        truffle migrate --network development --reset
        Write-Host '--- Deployment Script Finished ---'
        # Add Pause here ONLY if debugging the deployment window itself
        # Pause
    """
    # Command to launch PowerShell which then executes the script block
    command_list = [
        "powershell", "-Command",
        "Start-Process", "powershell", "-ArgumentList", f"{{ {ps_script_block_content} }}"
    ]

    try:
        print(f"   Executing via Start-Process with Script Block...")
        deployment_launcher_process = subprocess.Popen(command_list)
        print("   Waiting for deployment & .env update (approx 35s)...")
        time.sleep(25)
        exit_code = deployment_launcher_process.poll() # Check if launcher itself exited
        if exit_code is not None: print(f"   Warning: Deployment launcher process exited early (Code: {exit_code}).")
        print("✅ Deployment process launched (check separate window for status).")
        return deployment_launcher_process
    except FileNotFoundError: print(f"❌ Error: 'powershell' not found."); return None
    except Exception as e: print(f"❌ Error executing deployment command via Start-Process: {e}"); return None

# --- FIXED FUNCTION: start_smart_grid ---
def start_smart_grid():
    """Starts the Smart Grid simulation in a new PowerShell window."""
    print("🟡 Starting Smart Grid Simulation in new PowerShell window...")
    try:
        smart_grid_script_path = os.path.join(PROJECT_ROOT_DIR, "smart_grid.py")
        if not os.path.exists(smart_grid_script_path):
            print(f"❌ Error: smart_grid.py not found at {smart_grid_script_path}")
            return None

        # Assuming 'python' is in PATH for the new shell. Use full path if necessary.
        python_exe = "python"
        # Escape path for ArgumentList: Use outer single quotes, double internal single quotes for the path
        escaped_script_path = smart_grid_script_path.replace("'", "''")
        argument_string = f"'{python_exe} ''{escaped_script_path}'''" # Command for the new PS window

        command_list = [
            "powershell", "-Command",
            "Start-Process", "powershell",
            "-ArgumentList", argument_string
        ]

        print("   Executing via Start-Process...")
        process = subprocess.Popen(command_list)
        time.sleep(2)
        exit_code = process.poll()
        if exit_code is not None: print(f"   Warning: Smart Grid launcher exited early (Code: {exit_code}).")
        print("✅ Smart-Grid simulation should be running in a separate window.")
        return process
    except FileNotFoundError: print(f"❌ Error: 'powershell' not found."); return None
    except Exception as e: print(f"❌ Error starting Smart Grid via Start-Process: {e}"); return None
# --- END FIXED FUNCTION ---

async def main():
    # ... (Agent initialization and main loop remains the same) ...
    print("🟡 Initializing agents...")
    gui = GUIAgent("gui@localhost", "password")
    house = House("house@localhost", "password")
    grid = Grid("grid@localhost", "password")
    behavioral_segmentation_agent = BehavioralSegmentationAgent("behavioralsegmentation@localhost", "password")
    demand_response_agent = DemandResponseAgent("demandresponse@localhost", "password")
    negotiation_agent = NegotiationAgent("negotiation@localhost", "password")
    prediction_agent = PredictionAgent("prediction@localhost", "password")
    facilitating_agent = FacilitatingAgent("facilitating@localhost", "password")

    try:
        await asyncio.gather(
            gui.start(), house.start(), grid.start(),
            behavioral_segmentation_agent.start(), demand_response_agent.start(),
            negotiation_agent.start(), prediction_agent.start(), facilitating_agent.start()
        )
        print("✅ All agents started!")
        while True: await asyncio.sleep(3600)
    except asyncio.CancelledError: print("Agent startup cancelled.")
    except Exception as e: print(f"Error during agent execution: {e}")


# --- Main Execution Block ---
if __name__ == "__main__":
    print("🚀 Launching the Multi-Agent System...")
    processes_to_cleanup = []
    try:
        # Start inline processes
        spade_process = start_spade()
        if spade_process: processes_to_cleanup.append(("SPADE", spade_process))
        else: raise Exception("SPADE failed to start")

        streamlit_process = start_streamlit()
        if streamlit_process: processes_to_cleanup.append(("Streamlit", streamlit_process))
        else: raise Exception("Streamlit failed to start")

        # Start processes in separate windows
        ganache_process = start_ganache()
        if ganache_process: processes_to_cleanup.append(("Ganache Launcher", ganache_process))
        else: raise Exception("Ganache failed to start")

        deployment_process = deploy_smart_contract()
        if deployment_process: processes_to_cleanup.append(("Deployment Launcher", deployment_process))
        else: raise Exception("Deployment failed to start or complete")

        # --- Calls the UPDATED start_smart_grid ---
        smart_grid_process = start_smart_grid()
        if smart_grid_process: processes_to_cleanup.append(("SmartGrid Launcher", smart_grid_process))
        else: raise Exception("Smart Grid failed to start")
        # --- END ---

        print("✅ All external processes initiated.")
        print("🟡 Running Multi-Agent System...")
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n🛑 KeyboardInterrupt received. Shutting down...")
    except Exception as e:
         print(f"\n--- An error occurred during startup: {e} ---")
         import traceback
         traceback.print_exc()
    finally:
        print("--- Cleaning up external processes ---")
        for name, proc in reversed(processes_to_cleanup):
             print(f"   Terminating {name} (PID: {proc.pid})...")
             try:
                  proc.terminate()
                  try: proc.wait(timeout=3)
                  except subprocess.TimeoutExpired: print(f"   {name} force killing..."); proc.kill(); proc.wait(timeout=2)
                  print(f"   {name} terminated/killed.")
             except Exception as e_term: print(f"   Error terminating {name} (PID: {proc.pid}): {e_term}")
        print("✅ Cleanup attempt complete.")
    print("Exiting main script.")