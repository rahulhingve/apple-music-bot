import subprocess
import os

class MusicDownloader:
    def __init__(self, tool_path):
        self.tool_path = tool_path

    def download(self, music_url, track_numbers):
        os.chdir(self.tool_path)
        cmd = f"go run main.go --select {music_url}"
        
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        
        # Send track selection
        process.stdin.write(f"{track_numbers}\n")
        process.stdin.flush()
        
        # Wait for download to complete
        process.wait()
        
        return os.path.join(self.tool_path, "AM-DL downloads")
