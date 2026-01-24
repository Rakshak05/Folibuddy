import shutil
import os

def zip_portfolio(folder_path: str) -> str:
    """
    Create a ZIP archive from a portfolio folder.
    
    Args:
        folder_path: Path to the folder to zip
        
    Returns:
        str: Path to the created ZIP file
    """
    zip_path = folder_path.rstrip("/\\") + ".zip"
    shutil.make_archive(folder_path.rstrip("/\\"), 'zip', folder_path)
    return zip_path
