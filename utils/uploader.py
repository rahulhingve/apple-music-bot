import subprocess
import logging

logger = logging.getLogger(__name__)

def upload_to_gofile(file_path):
    try:
        logger.info(f"Starting upload of {file_path} to Gofile")
        # Run gofilepy command
        result = subprocess.run(
            f"gofilepy {file_path}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Upload failed: {result.stderr}")
            raise Exception("Gofile upload failed")
            
        # Extract URL from output
        for line in result.stdout.split('\n'):
            if 'Download page:' in line:
                url = line.split('https://')[1].strip()
                logger.info(f"Upload successful, URL: {url}")
                return url
                
        raise Exception("Could not find download URL in output")
                
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise Exception(f"Upload failed: {str(e)}")
