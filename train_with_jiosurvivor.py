import time
import logging
import sys
from resilient_downloader import ResilientDownloader
from jiosurvivor_monitor import NetworkHealthMonitor

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("NeuroStasis_Manager")

def main():
    logger.info("--- Starting NeuroStasis Protocol ---")
    
    # 1. Initialize the Monitor (The Brain)
    monitor = NetworkHealthMonitor()
    monitor.start_monitoring()

    # 2. Define the Target (Large Python File for testing)
    target_url = "https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe"
    downloader = ResilientDownloader(target_url)

    logger.info("Protocol Initiated: Downloading Dataset with Fault Tolerance...")
    
    # 3. Start the Resilient Download (The Engine)
    # The downloader handles its own retries, but relies on the system network
    success = downloader.download()

    if success:
        logger.info("✅ Data Ingestion Complete. Starting Model Training...")
        # Simulate Training Start
        time.sleep(1)
        logger.info("[GPU-BOUND] Training Epoch 1/50... [====      ]")
    else:
        logger.error("🛑 Ingestion Aborted manually or Fatal Error.")

    # 4. Cleanup
    monitor.stop()
    logger.info("System Shutdown.")

if __name__ == "__main__":
    main()