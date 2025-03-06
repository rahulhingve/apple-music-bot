import subprocess
import logging
import shlex
import os

logger = logging.getLogger(__name__)

def upload_to_gofile(file_path):
    try:
        logger.info(f"Starting upload of {file_path} to Gofile")
        
        # Create a safe file path by copying to a temporary location with a clean name
        temp_dir = "/tmp"
        temp_filename = "upload_" + str(hash(file_path)) + ".zip"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        try:
            # Copy file to temp location
            subprocess.run(f"cp {shlex.quote(file_path)} {shlex.quote(temp_path)}", shell=True, check=True)
            
            # Run gofilepy command with safe path
            result = subprocess.run(
                f"gofilepy {shlex.quote(temp_path)}",
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract URL from output
            for line in result.stdout.split('\n'):
                if 'Download page:' in line:
                    url = line.split('https://')[1].strip()
                    logger.info(f"Upload successful, URL: {url}")
                    return url
                    
            raise Exception("Could not find download URL in output")
                    
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except subprocess.CalledProcessError as e:
        logger.error(f"Upload process error: {e.stderr}")
        raise Exception(f"Upload failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise Exception(f"Upload failed: {str(e)}")
