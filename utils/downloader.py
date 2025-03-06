import subprocess
import os
import logging
import time

logger = logging.getLogger(__name__)

class MusicDownloader:
    def __init__(self, tool_path):
        self.tool_path = tool_path

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
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for the selection prompt
            output = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                logger.info(line.strip())
                output.append(line)
                if "select:" in line:
                    try:
                        # Wait a bit before sending input
                        time.sleep(1)
                        process.stdin.write(f"{track_numbers}\n")
                        process.stdin.flush()
                    except BrokenPipeError:
                        logger.error("Broken pipe while sending input")
                        process.terminate()
                        raise Exception("Failed to send track selection")
            
            # Get the final output and check for errors
            stdout, stderr = process.communicate()
            output.extend(stdout.splitlines() if stdout else [])
            
            if process.returncode != 0:
                error_msg = stderr if stderr else "Unknown error"
                logger.error(f"Process failed with return code {process.returncode}: {error_msg}")
                raise Exception(f"Download process failed: {error_msg}")

            # Verify download directory exists
            download_dir = os.path.join(self.tool_path, "AM-DL downloads")
            if not os.path.exists(download_dir):
                raise Exception("Download directory not found after process completion")

            return download_dir

        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")
        finally:
            # Ensure process is terminated
            if 'process' in locals() and process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
