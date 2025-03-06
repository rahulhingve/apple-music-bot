import subprocess
import os
import logging

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
                text=True
            )
            
            # Wait for the prompt
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                logger.info(line.strip())
                if "select:" in line:
                    # Found the prompt, send track numbers
                    process.stdin.write(f"{track_numbers}\n")
                    process.stdin.flush()
                    break
            
            # Continue reading output until process completes
            output, error = process.communicate()
            logger.info(output)
            
            if process.returncode != 0:
                logger.error(f"Download failed: {error}")
                raise Exception("Download process failed")

            return os.path.join(self.tool_path, "AM-DL downloads")

        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")
