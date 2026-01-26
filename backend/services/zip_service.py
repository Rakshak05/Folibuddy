import shutil
import os
import tempfile
from pathlib import Path

def zip_portfolio(folder_path: str, user_name: str = "Portfolio") -> str:
    """
    Create a ZIP archive from a portfolio folder with a named subfolder.
    
    Args:
        folder_path: Path to the portfolio folder to zip
        user_name: Name of the user (used for folder name inside ZIP)
        
    Returns:
        str: Path to the created ZIP file
    """
    # Clean the user name for use in folder/file names
    # Remove special characters and limit length
    safe_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')[:50]  # Limit to 50 chars
    
    if not safe_name:
        safe_name = "Portfolio"
    
    # Create a temporary directory for restructuring
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create the user-named folder inside temp dir
        user_folder = os.path.join(temp_dir, safe_name)
        os.makedirs(user_folder, exist_ok=True)
        
        # Copy all files from folder_path to the user-named folder
        for item in os.listdir(folder_path):
            source = os.path.join(folder_path, item)
            destination = os.path.join(user_folder, item)
            
            if os.path.isfile(source):
                shutil.copy2(source, destination)
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
        
        # Create zip file path
        zip_path = folder_path + ".zip"
        
        # Create the ZIP archive with the user-named folder inside
        shutil.make_archive(
            base_name=folder_path,
            format='zip',
            root_dir=temp_dir
        )
        
        print(f"Portfolio zipped at: {zip_path}")
        
        return zip_path
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
