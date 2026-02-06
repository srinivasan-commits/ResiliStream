import threading
import time
import requests
import logging

# --- Configuration ---
PING_TARGET = "http://clients3.google.com/generate_204" # Low bandwidth target
PING_INTERVAL = 2  # Check every 2 seconds
TIMEOUT = 3        # If no response in 3s, network is dead

logger = logging.getLogger("JioSurvivor_Monitor")

class NetworkHealthMonitor:
    def __init__(self):
        self.is_online = True
        self._running = False
        self._thread = None

    def start_monitoring(self):
        """Starts the background daemon thread."""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("Network Health Monitor: STARTED (Background)")

    def _monitor_loop(self):
        while self._running:
            try:
                # Use HEAD request for minimal data usage
                requests.head(PING_TARGET, timeout=TIMEOUT)
                if not self.is_online:
                    logger.info("✅ Network RECOVERED. Signal Stable.")
                self.is_online = True
            except requests.RequestException:
                if self.is_online:
                    logger.warning("❌ Network FAILED. Latency Critical.")
                self.is_online = False
            
            time.sleep(PING_INTERVAL)

    def get_status(self):
        return self.is_online

    def stop(self):
        self._running = False

