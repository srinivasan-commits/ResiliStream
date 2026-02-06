import os
import sys
import time
import signal
import logging
import argparse
import requests
from urllib.parse import urlparse

# --- Configuration ---
CHUNK_SIZE = 1024 * 1024  # 1 MB
CONNECT_TIMEOUT = 5       # Strict timeout for fast failure detection
READ_TIMEOUT = 10
MAX_RETRIES = 100         # High retry count for "Survival" mode
RETRY_DELAY = 3           # Quick retry
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("JioSurvivor_Core")

class ResilientDownloader:
    def __init__(self, url: str, output_dir: str = "."):
        self.url = url
        self.output_dir = output_dir
        self.filename = self._get_filename(url)
        self.filepath = os.path.join(output_dir, self.filename)
        self._running = True
        
        # Graceful Exit
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        sys.stdout.write("\n")
        logger.warning("Interrupt received. Pausing download safely...")
        self._running = False

    def _get_filename(self, url: str) -> str:
        parsed = urlparse(url)
        fname = os.path.basename(parsed.path)
        return fname if fname else "data_packet.bin"

    def download(self) -> bool:
        """
        Executes the download. Returns True if successful, False if stopped/failed.
        """
        existing_size = 0
        if os.path.exists(self.filepath):
            existing_size = os.path.getsize(self.filepath)
            logger.info(f"Resuming '{self.filename}' from {existing_size / (1024*1024):.2f} MB")
        else:
            logger.info(f"Initializing download: '{self.filename}'")

        headers = {'Range': f'bytes={existing_size}-', 'User-Agent': USER_AGENT}

        while self._running:
            try:
                with requests.get(self.url, headers=headers, stream=True, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)) as response:
                    if response.status_code == 416:
                        logger.info("File verification complete: Download finished.")
                        return True
                    
                    if response.status_code not in [200, 206]:
                        logger.error(f"Server Error {response.status_code}. Retrying...")
                        time.sleep(RETRY_DELAY)
                        continue

                    total_size = int(response.headers.get('content-length', 0)) + existing_size
                    mode = 'ab' if existing_size > 0 else 'wb'

                    with open(self.filepath, mode) as f:
                        start_time = time.time()
                        downloaded_this_session = 0
                        
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            if not self._running: break
                            if chunk:
                                f.write(chunk)
                                downloaded_this_session += len(chunk)
                                current_total = existing_size + downloaded_this_session
                                
                                # Progress Calculation
                                elapsed = time.time() - start_time
                                speed = (downloaded_this_session) / (elapsed + 0.1) / (1024 * 1024)
                                percent = (current_total / total_size) * 100 if total_size else 0
                                
                                sys.stdout.write(f"\r[IO-BOUND] Downloading... {percent:.2f}% | Speed: {speed:.2f} MB/s")
                                sys.stdout.flush()
                        
                        existing_size += downloaded_this_session

                if self._running:
                    sys.stdout.write("\n")
                    logger.info("Download Success.")
                    return True

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                sys.stdout.write("\n")
                logger.warning(f"Network Drop Detected. Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                if os.path.exists(self.filepath):
                    existing_size = os.path.getsize(self.filepath)
                    headers['Range'] = f'bytes={existing_size}-'
            
            except Exception as e:
                logger.critical(f"Fatal Error: {e}")
                return False
        
        return False

# Self-test block
if __name__ == "__main__":
    # Test with a small safe file
    dl = ResilientDownloader("https://proof.ovh.net/files/10Mb.dat")
    dl.download()