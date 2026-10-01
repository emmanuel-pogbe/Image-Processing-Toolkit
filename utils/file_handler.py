"""
File validation, sanitization, and security utilities for image and PDF uploads.
"""

from werkzeug.utils import secure_filename
import mimetypes
from PIL import Image
import os


def sanitize_filename(filename):
    """
    Sanitize filename using werkzeug's secure_filename.
    Returns safe filename or empty string if invalid.
    """
    return secure_filename(filename)


def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension against allowed list.
    
    Args:
        filename: The uploaded filename
        allowed_extensions: Set of allowed extensions (e.g., {'jpg', 'png', 'pdf'})
    
    Returns:
        (success: bool, error_message: str)
    """
    if '.' not in filename:
        return False, "File has no extension"
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        allowed_str = ', '.join(sorted(allowed_extensions)).upper()
        return False, f"File format not supported. Supported formats: {allowed_str}"
    
    return True, ""


def validate_file_size(file_path, max_size_mb=50):
    """
    Validate file size against limit.
    
    Args:
        file_path: Path to the file
        max_size_mb: Maximum file size in MB (default 50)
    
    Returns:
        (success: bool, error_message: str)
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    try:
        file_size = os.path.getsize(file_path)
        if file_size > max_size_bytes:
            return False, f"File size exceeds {max_size_mb}MB limit. Please upload a smaller file"
        return True, ""
    except OSError as e:
        return False, f"Error checking file size: {str(e)}"


def validate_mime_type(file_path, expected_mime_types):
    """
    Validate file MIME type.
    
    Args:
        file_path: Path to the file
        expected_mime_types: List or set of expected MIME types (e.g., ['image/jpeg', 'image/png'])
    
    Returns:
        (success: bool, error_message: str)
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type and mime_type not in expected_mime_types:
        return False, "File MIME type does not match expected format"
    
    return True, ""


def is_file_corrupted(file_path, file_type='image'):
    """
    Check if file is corrupted by attempting to open it.
    
    Args:
        file_path: Path to the file
        file_type: Type of file ('image' or 'pdf')
    
    Returns:
        (success: bool, error_message: str)
    """
    try:
        if file_type == 'image':
            with Image.open(file_path) as img:
                img.verify()
            return True, ""
        elif file_type == 'pdf':
            # Basic PDF validation - check if file starts with PDF header
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    return False, "File is corrupted or is not a valid PDF"
            return True, ""
    except Exception as e:
        if file_type == 'image':
            return False, "File is corrupted or cannot be read. Please upload a valid image file"
        elif file_type == 'pdf':
            return False, "PDF file is corrupted or cannot be processed. Please upload a valid PDF"
    
    return False, "Could not verify file integrity"


def validate_image_file(file_path, allowed_extensions):
    """
    Comprehensive validation for image files.
    
    Args:
        file_path: Path to the uploaded file
        allowed_extensions: Set of allowed image extensions
    
    Returns:
        (success: bool, error_message: str)
    """
    # Validate extension
    filename = os.path.basename(file_path)
    success, msg = validate_file_extension(filename, allowed_extensions)
    if not success:
        return False, msg
    
    # Validate file size
    success, msg = validate_file_size(file_path, max_size_mb=50)
    if not success:
        return False, msg
    
    # Validate file is not corrupted
    success, msg = is_file_corrupted(file_path, file_type='image')
    if not success:
        return False, msg
    
    return True, ""


def validate_pdf_file(file_path):
    """
    Comprehensive validation for PDF files.
    
    Args:
        file_path: Path to the uploaded PDF file
    
    Returns:
        (success: bool, error_message: str)
    """
    # Validate extension
    success, msg = validate_file_extension(os.path.basename(file_path), {'pdf'})
    if not success:
        return False, "File format not supported. Please upload a valid PDF file"
    
    # Validate file size
    success, msg = validate_file_size(file_path, max_size_mb=50)
    if not success:
        return False, msg
    
    # Validate file is not corrupted
    success, msg = is_file_corrupted(file_path, file_type='pdf')
    if not success:
        return False, msg
    
    return True, ""
