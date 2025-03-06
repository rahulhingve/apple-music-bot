import subprocess
import os
import logging
import time
from queue import Queue, Empty
from threading import Thread

logger = logging.getLogger(__name__)

class MusicDownloader:
    def __init__(self, tool_path):
        self.tool_path = tool_path

    def _enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def download(self, music_url, track_numbers):
        try:
            os.chdir(self.tool_path)
            
            # Start the download process - just the URL first
            logger.info(f"Starting download process for {music_url}")
            process = subprocess.Popen(
                f"go run main.go --select {music_url}",
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Set up queue and thread for non-blocking reads
            q = Queue()
            t = Thread(target=self._enqueue_output, args=(process.stdout, q))
            t.daemon = True
            t.start()

            # First wait for the table to be displayed (15 seconds max)
            logger.info("Waiting for track list to appear...")
            table_found = False
            start_time = time.time()
            
            while time.time() - start_time < 15:
                try:
                    while not q.empty():
                        line = q.get_nowait()
                        logger.info(line.strip())
                        if "TRACK NAME" in line:
                            table_found = True
                except Empty:
                    pass
                time.sleep(0.5)
                
            if not table_found:
                raise Exception("Track list not found")

            # Now wait for select prompt and send tracks
            logger.info("Waiting for select prompt...")
            time.sleep(2)  # Give it time to show the prompt
            
            while True:
                try:
                    line = q.get(timeout=5)
                    logger.info(line.strip())
                    if "select:" in line:
                        logger.info(f"Sending track selection: {track_numbers}")
                        time.sleep(1)  # Wait a bit before sending
                        process.stdin.write(f"{track_numbers}\n")
                        process.stdin.flush()
                        break
                except Empty:
                    continue

            # Wait for download to complete
            while process.poll() is None:
                try:
                    line = q.get(timeout=1)
                    logger.info(line.strip())
                    if "Completed:" in line and "Errors: 0" in line:
                        logger.info("Download completed successfully")
                        break
                except Empty:
                    continue

            # Verify success
            if process.returncode not in [None, 0]:
                stderr = process.stderr.read()
                raise Exception(f"Process failed: {stderr}")

            # Check download directory
            download_dir = os.path.join(self.tool_path, "AM-DL downloads")
            if not os.path.exists(download_dir):
                raise Exception("Download directory not found")

            return download_dir

        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")
        finally:
            if 'process' in locals():
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    pass
