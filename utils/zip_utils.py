import os
import shutil

def find_album_folder(download_dir):
    # Navigate through AM-DL downloads to find the album folder (2nd subfolder)
    for artist in os.listdir(download_dir):
        artist_path = os.path.join(download_dir, artist)
        if os.path.isdir(artist_path):
            for album in os.listdir(artist_path):
                return os.path.join(artist_path, album)
    return None

def create_zip(download_dir):
    album_path = find_album_folder(download_dir)
    if not album_path:
        return None
        
    zip_name = f"{os.path.basename(album_path)}.zip"
    zip_path = os.path.join(os.path.dirname(album_path), zip_name)
    
    shutil.make_archive(
        os.path.splitext(zip_path)[0],
        'zip',
        album_path
    )
    
    return zip_path
