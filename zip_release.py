import os
import shutil
from zipfile import ZipFile
import platform
from datetime import datetime

def zip_executable():
    # Get current date for version
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Determine system
    system = platform.system().lower()
    
    # Create zip name with date
    zip_name = f"TriviaRoyale-{system}-{date_str}.zip"
    
    # Directory containing the executable (PyInstaller output)
    dist_dir = "dist"
    
    if not os.path.exists(dist_dir):
        print(f"Error: {dist_dir} directory not found!")
        return
    
    try:
        with ZipFile(zip_name, 'w') as zipf:
            # Walk through the dist directory
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate path inside zip file
                    arcname = os.path.relpath(file_path, dist_dir)
                    print(f"Adding: {arcname}")
                    zipf.write(file_path, arcname)
        
        zip_size = os.path.getsize(zip_name) / (1024*1024)  # Convert to MB
        print(f"\nSuccessfully created: {zip_name}")
        print(f"Size: {zip_size:.2f} MB")
        
    except Exception as e:
        print(f"Error creating zip file: {e}")

if __name__ == "__main__":
    zip_executable()