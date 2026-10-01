"""
File cleanup and orphaned file management utilities.
"""

import os
import time
from datetime import datetime, timedelta


def safe_remove_file(file_path):
    """
    Safely remove a file with error handling.
    
    Args:
        file_path: Path to the file to remove
    
    Returns:
        (success: bool, error_message: str)
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True, f"Deleted: {file_path}"
    except PermissionError:
        return False, f"Permission denied: {file_path}"
    except OSError as e:
        return False, f"Error deleting {file_path}: {str(e)}"
    
    return False, f"File not found: {file_path}"


def cleanup_old_files(folder_path, max_age_hours=1):
    """
    Delete files older than specified age from a folder.
    
    Args:
        folder_path: Path to the folder to clean
        max_age_hours: Maximum age of files in hours (default 1 hour)
    
    Returns:
        (deleted_count: int, errors: list)
    """
    deleted_count = 0
    errors = []
    
    if not os.path.exists(folder_path):
        return 0, [f"Folder does not exist: {folder_path}"]
    
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isfile(file_path):
                file_age_seconds = current_time - os.path.getmtime(file_path)
                
                if file_age_seconds > max_age_seconds:
                    success, msg = safe_remove_file(file_path)
                    if success:
                        deleted_count += 1
                    else:
                        errors.append(msg)
    except Exception as e:
        errors.append(f"Error scanning folder {folder_path}: {str(e)}")
    
    return deleted_count, errors


def cleanup_on_startup(upload_folder, download_folder, max_age_hours=24):
    """
    Clean up old files on application startup.
    
    Args:
        upload_folder: Path to upload folder
        download_folder: Path to download folder
        max_age_hours: Maximum age of files to keep (default 24 hours)
    
    Returns:
        dict with cleanup results
    """
    results = {
        'upload_folder': {'deleted': 0, 'errors': []},
        'download_folder': {'deleted': 0, 'errors': []}
    }
    
    # Clean upload folder
    deleted, errors = cleanup_old_files(upload_folder, max_age_hours)
    results['upload_folder']['deleted'] = deleted
    results['upload_folder']['errors'] = errors
    
    # Clean download folder
    deleted, errors = cleanup_old_files(download_folder, max_age_hours)
    results['download_folder']['deleted'] = deleted
    results['download_folder']['errors'] = errors
    
    return results


def get_file_age_minutes(file_path):
    """
    Get the age of a file in minutes.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Age in minutes (float) or -1 if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            age_seconds = time.time() - os.path.getmtime(file_path)
            return age_seconds / 60
    except OSError:
        pass
    
    return -1
