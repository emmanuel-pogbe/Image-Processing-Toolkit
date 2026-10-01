"""
Image conversion engine with PIL-based format conversion and transformations.
"""

from PIL import Image
import os


def is_valid_image(file_path):
    """
    Check if file is a valid image by attempting to open it.
    
    Args:
        file_path: Path to the image file
    
    Returns:
        (success: bool, error_message: str)
    """
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True, ""
    except Image.UnidentifiedImageError:
        return False, "File is not a valid image or is corrupted"
    except Exception as e:
        return False, f"Error validating image: {str(e)}"


def get_image_dimensions(file_path):
    """
    Get image dimensions (width, height).
    
    Args:
        file_path: Path to the image file
    
    Returns:
        ((width, height), error_message) or (None, error_message) on failure
    """
    try:
        with Image.open(file_path) as img:
            return img.size, ""
    except Exception as e:
        return None, f"Error getting image dimensions: {str(e)}"


def get_image_format(file_path):
    """
    Get detected PIL format of image.
    
    Args:
        file_path: Path to the image file
    
    Returns:
        (format_string, error_message) or (None, error_message) on failure
    """
    try:
        with Image.open(file_path) as img:
            return img.format, ""
    except Exception as e:
        return None, f"Error detecting image format: {str(e)}"


def convert_image(input_path, output_path, output_format):
    """
    Convert image to specified output format.
    
    Args:
        input_path: Path to input image
        output_path: Path where converted image will be saved
        output_format: Target format (PNG, JPG, WebP, BMP)
    
    Returns:
        (success: bool, error_message: str, output_filename: str)
    """
    try:
        output_format = output_format.upper()
        
        # Validate output format
        if output_format not in ['PNG', 'JPG', 'WEBP', 'BMP']:
            return False, f"Unsupported output format: {output_format}", ""
        
        # Open image
        with Image.open(input_path) as img:
            # Handle transparency for JPG conversion
            if output_format == 'JPG' and img.mode in ('RGBA', 'LA', 'P'):
                img = flatten_transparency(img, 'JPG')
            elif output_format == 'BMP' and img.mode in ('RGBA', 'LA'):
                img = flatten_transparency(img, 'BMP')
            
            # Convert AVIF to standard format if needed
            if img.format == 'AVIF':
                img = img.convert('RGB')
            
            # Ensure proper mode for format
            if output_format in ['JPG', 'BMP'] and img.mode not in ['RGB', 'L']:
                img = img.convert('RGB')
            elif output_format == 'PNG' and img.mode not in ['RGBA', 'RGB', 'L', 'LA']:
                img = img.convert('RGB')
            elif output_format == 'WEBP' and img.mode not in ['RGBA', 'RGB', 'L']:
                img = img.convert('RGB')
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save with appropriate quality settings
            if output_format == 'JPG':
                img.save(output_path, 'JPEG', quality=85, optimize=True)
            elif output_format == 'WEBP':
                img.save(output_path, 'WEBP', quality=90)
            elif output_format == 'PNG':
                img.save(output_path, 'PNG', compress_level=9)
            elif output_format == 'BMP':
                img.save(output_path, 'BMP')
            
            return True, "", os.path.basename(output_path)
    
    except Exception as e:
        return False, f"Conversion failed: {str(e)}", ""


def flatten_transparency(image, target_format='JPG'):
    """
    Flatten transparency by compositing image onto white background.
    
    Args:
        image: PIL Image object
        target_format: Target format (determines background color)
    
    Returns:
        PIL Image with transparency flattened
    """
    try:
        # Create white background
        background_color = (255, 255, 255)  # White
        if image.mode == 'RGBA':
            # Extract alpha channel
            alpha = image.split()[3]
            # Paste image with alpha mask onto white background
            background = Image.new('RGB', image.size, background_color)
            background.paste(image.convert('RGB'), mask=alpha)
            return background
        elif image.mode == 'LA':
            # Grayscale with alpha
            background = Image.new('L', image.size, 255)
            background.paste(image.convert('L'), mask=image.split()[1])
            return background
        elif image.mode == 'P':
            # Palette mode - convert to RGBA first
            if 'transparency' in image.info:
                image = image.convert('RGBA')
                return flatten_transparency(image, target_format)
            else:
                return image.convert('RGB')
        return image
    
    except Exception as e:
        # If flattening fails, just convert to RGB
        return image.convert('RGB')


def rasterize_svg(input_path, output_path, size=1024):
    """
    Rasterize SVG to PNG at specified size.
    
    Note: This is a placeholder. Full SVG support requires cairosvg or other external tool.
    For now, we'll return an error message.
    
    Args:
        input_path: Path to SVG file
        output_path: Path where rasterized PNG will be saved
        size: Canvas size (default 1024x1024)
    
    Returns:
        (success: bool, error_message: str)
    """
    try:
        # Try to import cairosvg if available
        try:
            import cairosvg
            cairosvg.svg2png(
                url=input_path,
                write_to=output_path,
                output_width=size,
                output_height=size
            )
            return True, ""
        except ImportError:
            # Fallback: Try using PIL's built-in SVG support (limited)
            try:
                with Image.open(input_path) as img:
                    img = img.resize((size, size))
                    img.save(output_path, 'PNG')
                    return True, ""
            except:
                return False, "SVG rasterization requires cairosvg library. Install with: pip install cairosvg"
    
    except Exception as e:
        return False, f"SVG rasterization failed: {str(e)}"


def convert_avif(input_path, output_path, output_format):
    """
    Convert AVIF image to target format.
    Pillow 9.1+ has built-in AVIF support.
    
    Args:
        input_path: Path to AVIF file
        output_path: Path where converted image will be saved
        output_format: Target format (PNG, JPG, WebP, BMP)
    
    Returns:
        (success: bool, error_message: str)
    """
    try:
        with Image.open(input_path) as img:
            # AVIF should open normally with Pillow 9.1+
            if img.format != 'AVIF' and img.format is not None:
                return False, "Input file is not an AVIF image"
            
            # Use standard conversion
            return convert_image(input_path, output_path, output_format)
    
    except Exception as e:
        return False, f"AVIF conversion error: {str(e)}"


def get_conversion_filename(original_filename, target_format):
    """
    Generate output filename for converted image.
    Pattern: {original_basename}_{target_format}.{ext}
    
    Args:
        original_filename: Original filename
        target_format: Target format (PNG, JPG, WebP, BMP)
    
    Returns:
        Generated filename
    """
    base_name = os.path.splitext(original_filename)[0]
    ext_map = {
        'PNG': '.png',
        'JPG': '.jpg',
        'WEBP': '.webp',
        'BMP': '.bmp'
    }
    ext = ext_map.get(target_format.upper(), '.png')
    return f"{base_name}_{target_format}{ext}"
