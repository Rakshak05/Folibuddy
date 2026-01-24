import shutil
import os

def zip_portfolio(folder_path: str) -> str:
    """
    Create a ZIP archive from a portfolio folder.
    
    Args:
        folder_path: Path to the portfolio folder to zip
        
    Returns:
        str: Path to the created ZIP file
    """
    # Create zip file path (folder_path + ".zip")
    zip_path = folder_path + ".zip"
    
    # Use shutil.make_archive to create the zip file
    # The base_name should NOT include .zip extension
    # The format is 'zip'
    # The root_dir is the folder to zip
    shutil.make_archive(
        base_name=folder_path,
        format='zip',
        root_dir=folder_path
    )
    
    print(f"✅ Portfolio zipped at: {zip_path}")
    
    return zip_path
