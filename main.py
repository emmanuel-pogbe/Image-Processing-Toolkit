from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import os
from utils.file_handler import validate_image_file, validate_pdf_file, sanitize_filename
from utils.image_processor import convert_image, get_conversion_filename
from utils.pdf_processor import convert_pdf_to_docx, get_pdf_conversion_filename
from utils.cleanup import cleanup_on_startup

# Flask app initialization
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 52428800  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'images'
app.config['DOWNLOAD_FOLDER'] = 'converted_images'
app.config['TRACK_MODIFICATIONS'] = False

# Constants
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'jfif', 'bmp', 'svg', 'avif'}
ALLOWED_IMAGE_FORMATS = ['PNG', 'JPG', 'WebP', 'BMP']
ALLOWED_PDF_EXTENSIONS = {'pdf'}

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

# Cleanup old files on startup
cleanup_results = cleanup_on_startup(
    app.config['UPLOAD_FOLDER'],
    app.config['DOWNLOAD_FOLDER'],
    max_age_hours=24
)


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page route (Task 2.1)"""
    return render_template('index.html')


@app.route('/image-convert', methods=['GET', 'POST'])
def image_convert():
    """Image converter page and processing (Tasks 2.2 & 2.3)"""
    if request.method == "POST":
        # Validate file presence
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == "":
            return jsonify({"status": "error", "message": "File not selected"}), 400
        
        # Validate format parameter
        target_format = request.form.get('format', '').upper()
        if not target_format:
            return jsonify({"status": "error", "message": "Please select a target format"}), 400
        
        if target_format not in ALLOWED_IMAGE_FORMATS:
            return jsonify({"status": "error", "message": f"Invalid output format: {target_format}"}), 400
        
        # Validate file extension
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({
                "status": "error",
                "message": "File format not supported. Supported formats: JPG, JPEG, PNG, WebP, JFIF, BMP, SVG, AVIF"
            }), 400
        
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Validate file integrity
            success, error_msg = validate_image_file(upload_path, ALLOWED_IMAGE_EXTENSIONS)
            if not success:
                # Clean up invalid file
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return jsonify({"status": "error", "message": error_msg}), 400
            
            # Perform actual image conversion
            output_filename = get_conversion_filename(filename, target_format)
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            
            success, error_msg, converted_file = convert_image(upload_path, output_path, target_format)
            
            if not success:
                # Clean up uploaded file if conversion failed
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return jsonify({"status": "error", "message": error_msg}), 500
            
            # Clean up uploaded file after successful conversion
            if os.path.exists(upload_path):
                os.remove(upload_path)
            
            # Return success with download link
            return jsonify({
                "status": "success",
                "message": "Image converted successfully",
                "filename": output_filename,
                "download_url": url_for('download_converted_image', filename=output_filename, _external=False)
            }), 200
            
        except Exception as e:
            app.logger.error(f"Error in image conversion: {e}")
            return jsonify({"status": "error", "message": "An error occurred during conversion. Please try again"}), 500
    
    # GET request - render image converter page
    return render_template('image_converter.html', allowed_formats=ALLOWED_IMAGE_FORMATS)


@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    """PDF converter page (Tasks 2.4 & 2.5)"""
    if request.method == "POST":
        # Validate file presence
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == "":
            return jsonify({"status": "error", "message": "File not selected"}), 400
        
        # Validate file extension
        if not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
            return jsonify({
                "status": "error",
                "message": "File format not supported. Please upload a valid PDF file"
            }), 400
        
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Validate PDF file integrity
            success, error_msg = validate_pdf_file(upload_path)
            if not success:
                # Clean up invalid file
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return jsonify({"status": "error", "message": error_msg}), 400
            
            # Perform actual PDF to DOCX conversion
            output_filename = get_pdf_conversion_filename(filename)
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            
            success, error_msg, converted_file = convert_pdf_to_docx(upload_path, output_path)
            
            if not success:
                # Clean up uploaded file if conversion failed
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return jsonify({"status": "error", "message": error_msg}), 500
            
            # Clean up uploaded file after successful conversion
            if os.path.exists(upload_path):
                os.remove(upload_path)
            
            # Return success with download link
            return jsonify({
                "status": "success",
                "message": "PDF converted to Word successfully",
                "filename": output_filename,
                "download_url": url_for('download_converted_document', filename=output_filename, _external=False)
            }), 200
            
        except Exception as e:
            app.logger.error(f"Error in PDF conversion: {e}")
            return jsonify({"status": "error", "message": "An error occurred during conversion. Please try again"}), 500
    
    # GET request - render PDF converter page
    return render_template('pdf_converter.html')


@app.route('/converted_image/<filename>')
def download_converted_image(filename):
    """Download converted image and cleanup (Task 2.6)"""
    try:
        # Validate filename doesn't contain path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({"status": "error", "message": "Invalid filename"}), 400
        
        # Use secure_filename to validate
        safe_filename = secure_filename(filename)
        if safe_filename != filename:
            return jsonify({"status": "error", "message": "Invalid filename"}), 400
        
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        # Determine MIME type based on file extension
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
        mime_type = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
        
        response = send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=filename
        )
        
        # Register cleanup callback
        @response.call_on_close
        def cleanup():
            try:
                # Delete converted file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    app.logger.info(f"Deleted converted file: {file_path}")
                
                # Try to delete original upload (best effort)
                # In production, this would be tracked by the conversion engine
            except Exception as e:
                app.logger.exception(f"Error during cleanup: {e}")
        
        return response
    
    except Exception as e:
        app.logger.error(f"Error downloading file: {e}")
        return jsonify({"status": "error", "message": "An error occurred during download"}), 500


@app.route('/converted_document/<filename>')
def download_converted_document(filename):
    """Download converted PDF to DOCX (Task 2.6)"""
    try:
        # Validate filename doesn't contain path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({"status": "error", "message": "Invalid filename"}), 400
        
        # Use secure_filename to validate
        safe_filename = secure_filename(filename)
        if safe_filename != filename:
            return jsonify({"status": "error", "message": "Invalid filename"}), 400
        
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        response = send_file(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
        
        # Register cleanup callback
        @response.call_on_close
        def cleanup():
            try:
                # Delete converted file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    app.logger.info(f"Deleted converted document: {file_path}")
            except Exception as e:
                app.logger.exception(f"Error during cleanup: {e}")
        
        return response
    
    except Exception as e:
        app.logger.error(f"Error downloading document: {e}")
        return jsonify({"status": "error", "message": "An error occurred during download"}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({"status": "error", "message": "Page not found"}), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    """413 error handler for files exceeding MAX_CONTENT_LENGTH"""
    return jsonify({"status": "error", "message": "File size exceeds 50MB limit. Please upload a smaller file"}), 413


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    app.logger.error(f"Internal server error: {error}")
    return jsonify({"status": "error", "message": "An internal server error occurred"}), 500


if __name__ == '__main__':
    app.run(debug=True)
