import subprocess

def upload_to_gofile(file_path):
    try:
        result = subprocess.run(
            ['gofilepy', file_path],
            capture_output=True,
            text=True
        )
        
        # Extract URL from output
        for line in result.stdout.split('\n'):
            if 'Download page:' in line:
                return line.split('https://')[1].strip()
                
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return None
