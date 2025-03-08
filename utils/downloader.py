import subprocess
import os
import logging
import time
from queue import Queue, Empty
from threading import Thread
import psutil

logger = logging.getLogger(__name__)

class MusicDownloader:
    def __init__(self, tool_path):
        self.tool_path = tool_path
        self._process = None

    def _enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def download(self, music_url, track_numbers):
        try:
            os.chdir(self.tool_path)
            
            # Kill any zombie processes
            self._cleanup_zombie_processes()
            
            # Start process with resource limits
            self._process = subprocess.Popen(
                f"go run main.go --select {music_url}",
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Set CPU and memory limits
            process = psutil.Process(self._process.pid)
            process.nice(10)  # Lower priority
            
            # Set up queue and thread for non-blocking reads
            q = Queue()
            t = Thread(target=self._enqueue_output, args=(self._process.stdout, q))
            t.daemon = True
            t.start()

            # Wait for track list and prompt
            found_prompt = False
            start_time = time.time()
            
            while time.time() - start_time < 30:  # 30 seconds timeout
                try:
                    line = q.get(timeout=1)
                    logger.info(line.strip())
                    
                    # When we see the prompt message, send track numbers
                    if "Please select from the track options above" in line:
                        logger.info(f"Found prompt, sending track numbers: {track_numbers}")
                        time.sleep(0.5)  # Small delay before sending
                        self._process.stdin.write(f"{track_numbers}\n")
                        self._process.stdin.flush()
                        found_prompt = True
                        break
                except Empty:
                    continue

            if not found_prompt:
                raise Exception("Prompt not found within timeout")

            # Wait for download to complete
            while self._process.poll() is None:
                try:
                    line = q.get(timeout=1)
                    logger.info(line.strip())
                    if "Completed:" in line and "Errors: 0" in line:
                        logger.info("Download completed successfully")
                        break
                except Empty:
                    continue

            # Verify success
            if self._process.returncode not in [None, 0]:
                stderr = self._process.stderr.read()
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
            self._cleanup()

    def _cleanup_zombie_processes(self):
        """Clean up any zombie processes"""
        try:
            cmd = "pkill -f 'go run main.go'"
            subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
        except:
            pass

    def _cleanup(self):
        """Clean up resources"""
        if self._process:
            try:
                os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            except:
                pass
            self._process = None
