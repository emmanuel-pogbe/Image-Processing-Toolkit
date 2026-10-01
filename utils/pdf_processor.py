"""
PDF conversion engine for converting PDF to DOCX format.
"""

from pdf2docx import Converter
import os


def convert_pdf_to_docx(input_path, output_path):
    """
    Convert PDF document to DOCX (Word) format.
    
    Args:
        input_path: Path to input PDF file
        output_path: Path where converted DOCX will be saved
    
    Returns:
        (success: bool, error_message: str, output_filename: str)
    """
    try:
        # Validate input file exists
        if not os.path.exists(input_path):
            return False, "Input PDF file not found", ""
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Perform the conversion using pdf2docx Converter
        converter = Converter(input_path)
        converter.convert(output_path)
        converter.close()
        
        # Verify output file was created
        if not os.path.exists(output_path):
            return False, "PDF conversion failed - output file was not created", ""
        
        return True, "", os.path.basename(output_path)
    
    except Exception as e:
        return False, f"PDF to DOCX conversion failed: {str(e)}", ""


def get_pdf_conversion_filename(original_filename):
    """
    Generate output filename for converted PDF.
    Pattern: {original_basename}.docx
    
    Args:
        original_filename: Original PDF filename
    
    Returns:
        Generated DOCX filename
    """
    base_name = os.path.splitext(original_filename)[0]
    return f"{base_name}.docx"
