import subprocess
import os
import logging
import time
from queue import Queue
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

            # Wait for prompt and send input
            found_prompt = False
            while not found_prompt:
                try:
                    line = q.get(timeout=30)  # 30 second timeout
                    logger.info(line.strip())
                    if "select:" in line:
                        logger.info("Found selection prompt, sending track numbers")
                        time.sleep(0.5)  # Small delay before sending input
                        process.stdin.write(f"{track_numbers}\n")
                        process.stdin.flush()
                        found_prompt = True
                except Exception as e:
                    logger.error(f"Error while waiting for prompt: {str(e)}")
                    process.terminate()
                    raise Exception("Timeout waiting for selection prompt")

            # Continue reading output until process completes
            while process.poll() is None:
                try:
                    line = q.get(timeout=1)
                    logger.info(line.strip())
                    if "Completed:" in line:
                        logger.info("Download completed successfully")
                except:
                    pass  # No output within timeout

            if process.returncode != 0:
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
