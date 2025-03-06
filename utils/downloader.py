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
            
            # Start the download process
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

            # Wait for initial setup (10 seconds)
            logger.info("Waiting for Go process to initialize...")
            time.sleep(10)

            # Wait for prompt and send input
            found_prompt = False
            output_buffer = []
            max_attempts = 3
            attempt = 0

            while not found_prompt and attempt < max_attempts:
                try:
                    # Read all available output
                    while True:
                        try:
                            line = q.get_nowait()
                            output_buffer.append(line.strip())
                            logger.info(line.strip())
                            if "select:" in line:
                                found_prompt = True
                                break
                        except Empty:
                            break
                    
                    if found_prompt:
                        logger.info("Found selection prompt, sending track numbers")
                        time.sleep(1)  # Wait before sending input
                        process.stdin.write(f"{track_numbers}\n")
                        process.stdin.flush()
                    else:
                        attempt += 1
                        time.sleep(5)  # Wait 5 seconds before next attempt
                
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    attempt += 1
                    time.sleep(5)

            if not found_prompt:
                raise Exception("Failed to find selection prompt after multiple attempts")

            # Continue reading output until process completes
            while process.poll() is None:
                try:
                    line = q.get(timeout=1)
                    logger.info(line.strip())
                    if "Completed:" in line:
                        logger.info("Download completed successfully")
                        break
                except Empty:
                    continue

            # Check process result
            if process.returncode not in [None, 0]:
                stderr = process.stderr.read()
                raise Exception(f"Process failed: {stderr}")

            # Verify download directory exists
            download_dir = os.path.join(self.tool_path, "AM-DL downloads")
            if not os.path.exists(download_dir):
                raise Exception("Download directory not found after process completion")

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
