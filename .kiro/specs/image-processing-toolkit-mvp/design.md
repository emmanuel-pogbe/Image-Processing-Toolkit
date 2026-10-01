# Design Document: Image Processing Toolkit MVP

## 1. Architecture Overview

### 1.1 Application Structure

The Image Processing Toolkit MVP follows a modular Flask architecture with clear separation of concerns:

```
Image-Processing-Toolkit/
├── main.py                          # Flask application entry point
├── requirements.txt                 # Python dependencies
├── .gitignore
├── README.md
│
├── templates/                       # Jinja2 templates
│   ├── base.html                   # Base template with header/footer
│   ├── index.html                  # Home page
│   ├── image_converter.html        # Image conversion UI
│   ├── pdf_converter.html          # PDF conversion UI
│   └── error.html                  # Error page template
│
├── static/                         # Static assets
│   ├── css/
│   │   ├── main.css               # Base styles, typography, colors
│   │   ├── header.css             # Header and navigation styles
│   │   ├── footer.css             # Footer styles
│   │   ├── forms.css              # Form and input elements
│   │   ├── cards.css              # Card grid and hover effects
│   │   └── responsive.css         # Media queries and breakpoints
│   └── js/
│       ├── drag-drop.js           # Drag-and-drop functionality
│       ├── progress.js            # Upload progress bar
│       └── ui-interactions.js     # Micro-interactions and alerts
│
├── images/                        # Temporary upload folder
├── converted_images/              # Temporary download folder
│
└── utils/                         # Optional: helper modules
    ├── file_handler.py           # File validation and sanitization
    ├── image_processor.py        # Image conversion logic
    └── pdf_processor.py          # PDF conversion logic
```

### 1.2 Request-Response Flow

#### Image Conversion Flow:
1. User navigates to `/image-convert` (GET)
2. Frontend renders image converter page with drag-drop zone
3. User selects/drags file and chooses target format
4. Form submission triggers POST to `/image-convert`
5. Backend validates file (type, size, MIME)
6. Backend converts image to target format
7. Backend returns download link with HTTP 200
8. User downloads converted file
9. Backend deletes both original and converted files (immediate)
10. Backend cleanup process removes any orphaned files after 1 hour

#### PDF Conversion Flow:
1. User navigates to `/pdf-to-word` (GET)
2. Frontend renders PDF converter page with drag-drop zone
3. User selects/drags PDF file
4. Form submission triggers POST to `/pdf-to-word`
5. Backend validates PDF file
6. Backend converts PDF to DOCX using pdf2docx library
7. Backend returns download link with HTTP 200
8. User downloads converted file
9. Backend deletes original PDF after download completes
10. Backend cleanup process removes any orphaned files after 1 hour

### 1.3 File Handling Pipeline

```
[Upload] → [Validate] → [Store] → [Convert] → [Download] → [Cleanup]
   ↓          ↓           ↓         ↓           ↓           ↓
Check     Verify MIME  Save to   Process    Generate    Delete
extension type & size  temp      file       link        files
          Check        folder                           24hr/
          file size                                     5min
                                                        (abort)
```

**Key Points:**
- Uploaded files stored in `images/` folder with sanitized names
- Converted files stored in `converted_images/` folder
- Immediate deletion after download completes
- 1-hour retention for completed conversions (fallback cleanup)
- 5-minute cleanup for aborted downloads
- Full cleanup on app restart (24-hour threshold)

---

## 2. Frontend Architecture

### 2.1 Static Folder Structure

```
static/
├── css/
│   ├── main.css              # 300-400 lines
│   │   - Color palette definitions
│   │   - Typography rules
│   │   - Base element styles
│   │   - Utility classes
│   │
│   ├── header.css            # 150-200 lines
│   │   - Sticky header positioning
│   │   - Navigation menu layout
│   │   - Logo styling
│   │   - Mobile hamburger menu
│   │
│   ├── footer.css            # 150-200 lines
│   │   - Sticky footer positioning
│   │   - Multi-column layout
│   │   - Link styling
│   │   - Copyright section
│   │
│   ├── forms.css             # 200-300 lines
│   │   - Input field styling
│   │   - Dropdown/select styling
│   │   - Button variants (primary, secondary)
│   │   - Error state styling
│   │   - Drag-drop zone styling
│   │
│   ├── cards.css             # 100-150 lines
│   │   - Card grid layout
│   │   - Card component styles
│   │   - Hover effects and shadows
│   │   - Card header/footer sections
│   │
│   └── responsive.css        # 300-400 lines
│       - Mobile breakpoint (320px-767px)
│       - Tablet breakpoint (768px-1023px)
│       - Desktop breakpoint (1024px+)
│       - All responsive overrides
│
└── js/
    ├── drag-drop.js          # Drag-and-drop event handling
    ├── progress.js           # Upload progress bar
    └── ui-interactions.js    # Alerts, focus management
```

### 2.2 Template Organization and Inheritance

**Base Template Pattern (base.html):**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Image Processing Toolkit{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/header.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/footer.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/forms.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/cards.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/responsive.css') }}">
</head>
<body>
    {% include 'components/header.html' %}
    
    <main class="main-content">
        {% if messages %}
            {% for message in get_flashed_messages(with_categories=true) %}
                {% include 'components/alert.html' %}
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    {% include 'components/footer.html' %}
    
    <script src="{{ url_for('static', filename='js/drag-drop.js') }}"></script>
    <script src="{{ url_for('static', filename='js/progress.js') }}"></script>
    <script src="{{ url_for('static', filename='js/ui-interactions.js') }}"></script>
</body>
</html>
```

**Template Hierarchy:**
- `base.html` → Common header, footer, CSS imports
- `index.html` → Extends base, home page content
- `image_converter.html` → Extends base, image conversion UI
- `pdf_converter.html` → Extends base, PDF conversion UI
- Component templates in `components/` subdirectory

### 2.3 Drag-and-Drop Implementation

**File:** `static/js/drag-drop.js`

```javascript
// Key behaviors:
// 1. dragover event: Apply visual highlight (blue border + light bg)
// 2. dragleave event: Remove highlight
// 3. drop event: Extract file(s) and trigger validation
// 4. File input change event: Validate and display file info
// 5. Validation: Check extension, size, MIME type

Features:
- Visual feedback during drag
- File preview (name, size display)
- Format validation before upload
- Single file selection (no multiple)
- Accessible via click input fallback
```

### 2.4 Progress Bar Implementation

**File:** `static/js/progress.js`

```javascript
// XMLHttpRequest upload progress tracking:
// 1. xhr.upload.addEventListener('progress', ...)
// 2. Calculate percentage: (event.loaded / event.total) * 100
// 3. Update progress bar width: style.width = percentage + '%'
// 4. Display percentage text: "45%" etc.
// 5. Complete/Error states

Visual states:
- 0%: Gray (#CCCCCC)
- 1-99%: Blue gradient (#0066FF)
- 100%: Green (#00CC00)
- Error: Red (#FF4444)
```

---

## 3. Backend Routes Design

### 3.1 Route Definitions

#### GET /
**Purpose:** Render home page with tool card grid

**Response:**
- Status: 200 OK
- Content-Type: text/html
- Body: Rendered `index.html` with hero section and tool cards

**Error Handling:**
- No validation needed
- Server errors: 500 with error page

---

#### GET /image-convert
**Purpose:** Render image conversion page

**Response:**
- Status: 200 OK
- Content-Type: text/html
- Body: Rendered `image_converter.html` with drag-drop zone, format selector, upload button

**Parameters:** None

**Error Handling:**
- No validation needed

---

#### POST /image-convert
**Purpose:** Process image conversion request

**Request:**
```
Headers:
  Content-Type: multipart/form-data

Body:
  - file: File object (binary)
  - format: String (PNG|JPG|WebP|BMP)
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Conversion successful! Your file is ready for download",
  "download_url": "/converted_image/<filename>.png",
  "filename": "photo_PNG.png"
}
```
- Status: 200 OK
- Content-Type: application/json

**Response (Validation Error):**
```json
{
  "status": "error",
  "message": "File format not supported. Supported formats: JPG, JPEG, PNG, WebP, JFIF, BMP, SVG, AVIF"
}
```
- Status: 400 Bad Request
- Content-Type: application/json

**Error Messages:**
- Unsupported extension: "File format not supported..."
- Corrupted file: "File is corrupted or cannot be read..."
- File size exceeded: "File size exceeds 50MB limit..."
- Conversion failure: "Conversion failed. Please try again or contact support"
- No format selected: "Please select a target format"

**Validation Steps:**
1. Check file is present in request
2. Check file extension against ALLOWED_EXTENSIONS
3. Check file size <= 50MB
4. Check MIME type matches extension
5. Attempt to open file with PIL to verify integrity
6. Check format parameter is valid output format

---

#### GET /pdf-to-word
**Purpose:** Render PDF converter page

**Response:**
- Status: 200 OK
- Content-Type: text/html
- Body: Rendered `pdf_converter.html` with drag-drop zone and upload button

**Error Handling:**
- No validation needed

---

#### POST /pdf-to-word
**Purpose:** Process PDF-to-Word conversion request

**Request:**
```
Headers:
  Content-Type: multipart/form-data

Body:
  - file: File object (binary, .pdf)
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Conversion successful! Your file is ready for download",
  "download_url": "/converted_document/<filename>.docx",
  "filename": "document.docx"
}
```
- Status: 200 OK
- Content-Type: application/json

**Response (Validation Error):**
```json
{
  "status": "error",
  "message": "File format not supported. Please upload a valid PDF file"
}
```
- Status: 400 Bad Request
- Content-Type: application/json

**Error Messages:**
- Wrong format: "File format not supported. Please upload a valid PDF file"
- Corrupted PDF: "PDF file is corrupted or cannot be processed. Please upload a valid PDF"
- Password protected: "PDF is password-protected. Please remove the protection and try again"
- File size exceeded: "File size exceeds 50MB limit. Please upload a smaller PDF"
- Conversion failure: "An error occurred during conversion. Please try again"

**Validation Steps:**
1. Check file is present in request
2. Check file extension is .pdf (case-insensitive)
3. Check file size <= 50MB
4. Check MIME type is application/pdf
5. Attempt to open PDF with pdf2docx to verify validity
6. Check for password protection

---

### 3.2 Response Format Strategy

**Success Response Pattern:**
```python
{
    'status': 'success',
    'message': 'User-friendly message',
    'data': {...}  # Optional additional data
}
```

**Error Response Pattern:**
```python
{
    'status': 'error',
    'message': 'User-friendly error message'
}
```

**HTTP Status Codes:**
- 200: Successful conversion
- 400: Validation error (bad input)
- 500: Internal server error
- 422: Unprocessable entity (file corrupted after upload)

---

## 4. Database/File Storage Design

### 4.1 Temporary File Management

**Upload Folder:** `images/`
- Purpose: Store uploaded files during processing
- Naming: `{sanitized_filename}_{timestamp}.{ext}` (to prevent collisions)
- Cleanup: Deleted immediately after download completes

**Download Folder:** `converted_images/`
- Purpose: Store converted files ready for download
- Naming: `{original_basename}_{format}.{ext}`
  - Example: `photo_PNG.png`, `document.docx`
- Cleanup: 
  - Deleted immediately after download completes
  - Periodic cleanup: 1 hour retention for orphaned files
  - Full cleanup on app restart: Remove files older than 24 hours

**Temporary File Isolation:**
- Both folders isolated from web root
- No direct file access via URL traversal
- Files served only through download handler

### 4.2 File Naming Conventions

**Image Conversion:**
```
Input:  photo.jpg
Output: photo_PNG.png  (if converting to PNG)
        photo_JPG.jpg  (if converting to JPG)
        photo_WebP.webp
        photo_BMP.bmp
```

**PDF Conversion:**
```
Input:  document.pdf
Output: document.docx
```

**Sanitization:**
- Apply `secure_filename()` to all uploads
- Remove special characters, path traversal attempts
- Maintain original basename for user context
- Add format suffix for clarity

### 4.3 Cleanup Mechanism

**Immediate Cleanup (Post-Download):**
```python
@response.call_on_close
def cleanup():
    # Delete uploaded file
    os.remove(original_upload_path)
    # Delete converted file
    os.remove(converted_file_path)
```

**Periodic Cleanup (Background Task):**
- Runs every hour or on demand
- Deletes files in `images/` and `converted_images/` older than 1 hour
- Logs cleanup actions for monitoring

**Startup Cleanup:**
```python
# On app startup:
# 1. Scan images/ folder
# 2. Delete files older than 24 hours
# 3. Scan converted_images/ folder
# 4. Delete files older than 24 hours
```

**Abort Scenario (5-minute window):**
- If user closes download without completing
- Cleanup task detects orphaned file after 5 minutes
- Removes both original and converted files

---

## 5. Image Conversion Engine

### 5.1 Input Format Support Matrix

| Format | Extension | MIME Type | Support |
|--------|-----------|-----------|---------|
| JPEG   | .jpg, .jpeg, .jfif | image/jpeg | ✓ (Full) |
| PNG    | .png | image/png | ✓ (Full) |
| WebP   | .webp | image/webp | ✓ (Full) |
| BMP    | .bmp | image/bmp | ✓ (Full) |
| SVG    | .svg | image/svg+xml | ✓ (Rasterize) |
| AVIF   | .avif | image/avif | ✓ (Decode) |
| GIF    | .gif | image/gif | ✓ (Convert) |

### 5.2 Output Format Options

- **PNG**: Lossless, preserves transparency, larger file size
- **JPG**: Lossy compression (85% quality), no transparency support, smaller file size
- **WebP**: Modern format, 90% quality, hybrid compression, good file size
- **BMP**: Uncompressed, no compression, larger file size, basic support

### 5.3 Format-Specific Handlers

**Transparency Handling (PNG → JPG):**
```python
def convert_png_to_jpg(image_path, output_path):
    image = Image.open(image_path)
    
    # If image has transparency (RGBA mode)
    if image.mode == 'RGBA':
        # Create white background
        background = Image.new('RGB', image.size, (255, 255, 255))
        # Paste image with alpha channel as mask
        background.paste(image, mask=image.split()[3])
        image = background
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Save with quality setting
    image.save(output_path, 'JPEG', quality=85)
```

**SVG Rasterization (SVG → PNG/JPG/WebP/BMP):**
```python
def convert_svg_to_raster(svg_path, output_path, output_format, size=1024):
    # Use PIL or external library to rasterize
    # Default size: 1024x1024 pixels
    # Step 1: Render SVG to raster at specified size
    # Step 2: Convert to target format
    # Note: May require external tool like cairosvg
    
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    # ... SVG parsing and rendering logic
    image.save(output_path, output_format.upper())
```

**AVIF Decoding (AVIF → target format):**
```python
def convert_avif_to_target(avif_path, output_path, output_format):
    # PIL 9.1+ has AVIF support
    # Step 1: Open AVIF file with PIL
    image = Image.open(avif_path)
    # Step 2: Handle transparency based on target format
    # Step 3: Save to target format
    image.save(output_path, output_format.upper())
```

### 5.4 Quality Settings

**WebP Conversion:**
```python
image.save(output_path, 'WebP', quality=90)
```
- Quality: 90% (balance between file size and visual quality)
- Lossy compression for efficiency

**JPG Conversion:**
```python
image.save(output_path, 'JPEG', quality=85)
```
- Quality: 85% (standard web quality)
- Lossy compression

**PNG Conversion:**
```python
image.save(output_path, 'PNG', compress_level=9)
```
- Lossless compression (level 9 = maximum)
- No quality loss

**BMP Conversion:**
```python
image.save(output_path, 'BMP')
```
- No compression (uncompressed)

### 5.5 Error Handling Strategy

**Validation Errors (400 response):**
- Invalid file type
- File size exceeded
- MIME type mismatch
- File not found
- Format not selected

**Processing Errors (422/500 response):**
- File corrupted during conversion
- PIL cannot open file
- Memory insufficient
- Format conversion unsupported
- Disk space exceeded

**User-Friendly Messages:**
- "File format not supported. Supported formats: JPG, JPEG, PNG, WebP, JFIF, BMP, SVG, AVIF"
- "File is corrupted or cannot be read. Please upload a valid image file"
- "Conversion failed. Please try again or contact support"

---

## 6. PDF-to-Word Conversion Engine

### 6.1 pdf2docx Library Usage

```python
from pdf2docx import convert

def convert_pdf_to_docx(pdf_path, docx_path):
    """Convert PDF to DOCX using pdf2docx library"""
    try:
        convert(pdf_path, docx_path)
        return True
    except Exception as e:
        app.logger.error(f"PDF conversion error: {e}")
        return False
```

**Library:** `pdf2docx==0.5.13`
- Handles multi-page PDFs
- Preserves basic formatting
- Extracts text and tables
- Processes images where possible

### 6.2 Multi-Page Handling

**Processing:**
1. pdf2docx automatically processes all pages
2. Creates single DOCX output with all content
3. Page breaks preserved between original PDF pages

**Performance:**
- 100+ page PDFs processed within 30 seconds
- Streaming conversion for large files
- Memory management for large documents

**Validation:**
```python
# Check if PDF is valid before conversion
try:
    from pdf2docx import PDF
    pdf = PDF(pdf_path)
    page_count = len(pdf)
    pdf.close()
    
    if page_count == 0:
        raise ValueError("PDF has no pages")
    
    return True
except Exception as e:
    if "encrypted" in str(e).lower():
        # Password protected
        return False
    # Other corruption error
    return False
```

### 6.3 Formatting Preservation Strategy

**Supported Formatting:**
- Text formatting: Bold, italic, underline (where possible)
- Paragraph formatting: Alignment, spacing
- Tables: Converted to DOCX table format
- Images: Embedded in DOCX where extracted

**Limitations:**
- Complex layouts may not transfer perfectly
- Some fonts may not be available in Word
- Advanced PDF features (forms, annotations) not supported
- Color information preserved for text only

**Post-Processing:**
```python
# Optional: Post-process DOCX for enhanced formatting
from docx import Document

def enhance_docx_formatting(docx_path):
    doc = Document(docx_path)
    
    # Ensure consistent formatting
    # Fix paragraph spacing
    # Verify table structures
    # Validate embedded content
    
    doc.save(docx_path)
```

### 6.4 Error Handling for Protected PDFs

**Detection:**
```python
def is_pdf_protected(pdf_path):
    """Check if PDF is password-protected"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return pdf_reader.is_encrypted
    except:
        # Fallback: attempt to convert, catch encryption error
        try:
            from pdf2docx import convert
            convert(pdf_path, 'test_output.docx')
            return False
        except Exception as e:
            if "encrypted" in str(e).lower():
                return True
            raise
```

**Error Message:**
- "PDF is password-protected. Please remove the protection and try again"

**Other PDF Errors:**
- Corrupted: "PDF file is corrupted or cannot be processed. Please upload a valid PDF"
- Unsupported format: "PDF format not recognized. Please upload a valid PDF file"

---

## 7. UI/UX Component Design

### 7.1 Header Component

**Structure:**
```html
<header class="header">
    <div class="header-content">
        <div class="logo-section">
            <img src="/static/logo.png" alt="Logo" class="logo">
            <span class="app-title">Image Processing Toolkit</span>
        </div>
        
        <nav class="nav-menu">
            <a href="/" class="nav-link" aria-current="page">Home</a>
            <a href="/image-convert" class="nav-link">Image Tools</a>
            <a href="/pdf-to-word" class="nav-link">PDF Tools</a>
        </nav>
        
        <div class="auth-buttons">
            <button class="btn btn-secondary">Sign In</button>
            <button class="btn btn-primary">Sign Up</button>
        </div>
        
        <!-- Mobile hamburger menu -->
        <button class="hamburger" aria-label="Toggle menu" aria-expanded="false">
            <span></span>
            <span></span>
            <span></span>
        </button>
    </div>
</header>
```

**Styling:**
- Position: `position: sticky; top: 0;`
- Background: Vibrant blue `#0066FF`
- Text color: White `#FFFFFF`
- Z-index: 1000 (above all content)
- Height: 64px (desktop), 56px (mobile)
- Flexbox layout for alignment

**Responsive:**
- Desktop: Inline navigation, visible auth buttons
- Tablet: Inline navigation, visible auth buttons
- Mobile: Hidden navigation (hamburger menu), collapsed auth buttons

---

### 7.2 Footer Component

**Structure:**
```html
<footer class="footer">
    <div class="footer-content">
        <!-- Product Links -->
        <div class="footer-column">
            <h3>Product</h3>
            <ul>
                <li><a href="/image-convert">Image Converter</a></li>
                <li><a href="/pdf-to-word">PDF Converter</a></li>
                <li><a href="/feature-requests">Feature Requests</a></li>
            </ul>
        </div>
        
        <!-- Company Info -->
        <div class="footer-column">
            <h3>Company</h3>
            <ul>
                <li><a href="/about">About Us</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/blog">Blog</a></li>
            </ul>
        </div>
        
        <!-- Legal Links -->
        <div class="footer-column">
            <h3>Legal</h3>
            <ul>
                <li><a href="/privacy">Privacy Policy</a></li>
                <li><a href="/terms">Terms of Service</a></li>
                <li><a href="/cookies">Cookie Policy</a></li>
            </ul>
        </div>
    </div>
    
    <div class="footer-bottom">
        <p>&copy; 2024 Image Processing Toolkit. All rights reserved.</p>
    </div>
</footer>
```

**Styling:**
- Background: Vibrant blue `#0066FF`
- Text color: White `#FFFFFF`
- Multi-column layout (CSS Grid)
- Position: `position: relative;` (not sticky, at bottom of page)
- Padding: 48px 24px 24px (mobile to desktop)

---

### 7.3 Home Page Layout

**Hero Section:**
```html
<section class="hero">
    <div class="hero-content">
        <h1>Process Your Images and Documents Online</h1>
        <p class="hero-subtitle">Fast, simple, and secure conversion tools</p>
        <button class="btn btn-primary btn-large">Get Started</button>
    </div>
</section>
```

**Tool Card Grid:**
```html
<section class="tools-section">
    <h2>Our Tools</h2>
    
    <div class="cards-grid">
        <!-- Image Converter Card -->
        <div class="card">
            <div class="card-header">
                <img src="/static/icon-image.svg" alt="Image">
                <h3>Image Converter</h3>
            </div>
            <p class="card-description">
                Convert images between PNG, JPG, WebP, and BMP formats
            </p>
            <a href="/image-convert" class="btn btn-primary">Start Converting</a>
        </div>
        
        <!-- PDF to Word Card -->
        <div class="card">
            <div class="card-header">
                <img src="/static/icon-pdf.svg" alt="PDF">
                <h3>PDF to Word</h3>
            </div>
            <p class="card-description">
                Convert PDF documents to editable Word format
            </p>
            <a href="/pdf-to-word" class="btn btn-primary">Convert PDF</a>
        </div>
    </div>
</section>
```

**Styling:**
- Hero section: Full viewport height or min-height 400px
- Text alignment: Center
- Card grid: 2 columns (desktop), 1 column (mobile/tablet)
- Cards: 300px width (desktop), responsive (mobile)
- Spacing: 32px between cards, 48px between sections

---

### 7.4 Image Converter Page

**Layout:**
```html
<div class="converter-container">
    <h1>Image Converter</h1>
    <p class="page-subtitle">Convert images to PNG, JPG, WebP, or BMP</p>
    
    <form id="imageForm" class="converter-form">
        <!-- Drag-Drop Zone -->
        <div class="drop-zone" id="dropZone">
            <svg class="upload-icon" width="48" height="48"><!-- upload icon --></svg>
            <p>Drag and drop your image here or click to select</p>
            <input type="file" id="imageInput" class="file-input" accept="image/*">
        </div>
        
        <!-- Selected File Display -->
        <div id="fileInfo" class="file-info" style="display: none;">
            <p id="fileName"></p>
            <p id="fileSize"></p>
        </div>
        
        <!-- Format Selector -->
        <div class="form-group">
            <label for="formatSelect">Convert to:</label>
            <select id="formatSelect" name="format" required>
                <option value="">-- Select Format --</option>
                <option value="PNG" selected>PNG</option>
                <option value="JPG">JPG</option>
                <option value="WebP">WebP</option>
                <option value="BMP">BMP</option>
            </select>
        </div>
        
        <!-- Progress Bar -->
        <div id="progressContainer" class="progress-container" style="display: none;">
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill"></div>
            </div>
            <p id="progressText">0%</p>
        </div>
        
        <!-- Upload Button -->
        <button type="submit" class="btn btn-primary btn-large">Upload</button>
    </form>
    
    <!-- Success Alert -->
    <div id="successAlert" class="alert alert-success" style="display: none;">
        <p>Conversion successful! Your file is ready for download</p>
        <a id="downloadLink" href="#" class="btn btn-success">
            <span>Download</span>
        </a>
    </div>
</div>
```

**Styling:**
- Container width: 600px max (desktop), full width with padding (mobile)
- Drop zone: 250px height (desktop), 150px (mobile)
- Form group margin: 24px
- Buttons: Full width on mobile, fixed width on desktop

---

### 7.5 PDF Converter Page

**Layout:** (Similar structure to Image Converter)
```html
<div class="converter-container">
    <h1>PDF to Word Converter</h1>
    <p class="page-subtitle">Convert PDF documents to editable Word format</p>
    
    <form id="pdfForm" class="converter-form">
        <!-- Drag-Drop Zone (accepts only PDF) -->
        <!-- Selected File Display -->
        <!-- Progress Bar -->
        <!-- Upload Button -->
    </form>
    
    <!-- Success/Error Alerts -->
</div>
```

---

### 7.6 Alert Components

**Error Alert:**
```html
<div class="alert alert-error" role="alert" aria-live="assertive">
    <div class="alert-content">
        <svg class="alert-icon"><!-- error icon --></svg>
        <p id="errorMessage">Error message content</p>
    </div>
    <button class="alert-close" aria-label="Close alert">&times;</button>
</div>
```

**Success Alert:**
```html
<div class="alert alert-success" role="alert" aria-live="polite">
    <div class="alert-content">
        <svg class="alert-icon"><!-- success icon --></svg>
        <p>Conversion successful! Your file is ready for download</p>
    </div>
    <a href="/download/file.png" class="btn btn-success">Download</a>
</div>
```

**Styling:**
- Error: Red background `#FFE5E5`, red text `#FF4444`
- Success: Green background `#E5FFE5`, green text `#00CC00`
- Padding: 16px
- Border-radius: 4px
- Dismissible (close button)

---

### 7.7 Card Component

**Structure:**
```html
<div class="card">
    <div class="card-header">
        <h3>Card Title</h3>
    </div>
    <div class="card-body">
        <p>Card content description</p>
    </div>
    <div class="card-footer">
        <a href="#" class="btn btn-primary">Action</a>
    </div>
</div>
```

**Styling:**
- Background: Light gray `#F5F5F5`
- Border-radius: 8px
- Box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1)
- Padding: 24px
- Hover effects:
  - Shadow increase: 0 4px 16px rgba(0, 0, 0, 0.15)
  - Scale: transform: scale(1.02)
  - Transition: 200ms ease-out

---

## 8. CSS Design

### 8.1 Color Palette

| Purpose | Color | Hex Value | Usage |
|---------|-------|-----------|-------|
| Primary | Vibrant Blue | #0066FF | Headers, buttons, links, accents |
| Background | White | #FFFFFF | Main content areas |
| Secondary BG | Light Gray | #F5F5F5 | Cards, sections |
| Text | Dark Gray | #333333 | Body text, headings |
| Error | Red | #FF4444 | Error messages, validation |
| Success | Green | #00CC00 | Success messages, confirmations |
| Border | Medium Gray | #CCCCCC | Form inputs, dividers |
| Disabled | Light Gray | #E0E0E0 | Disabled buttons, inactive states |

### 8.2 Typography

**Font Family:**
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
```

**Heading Hierarchy:**
- H1: 28-32px, font-weight 700 (bold), line-height 1.2
- H2: 24-28px, font-weight 700, line-height 1.3
- H3: 18-22px, font-weight 600, line-height 1.4
- H4: 16-18px, font-weight 600, line-height 1.5

**Body Text:**
- Font size: 14-16px
- Line-height: 1.6
- Font-weight: 400 (normal)
- Color: #333333

**Link Text:**
- Color: #0066FF (vibrant blue)
- Text-decoration: none (on normal state)
- Text-decoration: underline (on hover)

### 8.3 Responsive Breakpoints

**Mobile (320px - 767px):**
- Single column layout
- Full-width elements
- Hamburger navigation
- Minimum touch target: 44x44px
- Font size minimum: 16px
- Stack cards vertically

**Tablet (768px - 1023px):**
- Two-column layout
- Inline navigation
- Two-column card grid
- Adjusted spacing

**Desktop (1024px+):**
- Multi-column layouts
- Full navigation visible
- Two-column card grid with centered content
- Maximum container width: 1200px

### 8.4 Spacing Scale

```css
/* 8px baseline scale */
$spacing-xs:  4px;    /* 0.25rem */
$spacing-sm:  8px;    /* 0.5rem */
$spacing-md:  16px;   /* 1rem */
$spacing-lg:  24px;   /* 1.5rem */
$spacing-xl:  32px;   /* 2rem */
$spacing-2xl: 48px;   /* 3rem */
$spacing-3xl: 64px;   /* 4rem */
```

**Usage:**
- Padding inside components: 16px-24px
- Margin between sections: 32px-48px
- Gap between grid items: 24px
- Form input padding: 12px-16px

### 8.5 Modular CSS Organization

**main.css (~400 lines):**
```css
/* 1. CSS Reset */
* { margin: 0; padding: 0; box-sizing: border-box; }

/* 2. Color Variables */
:root {
    --color-primary: #0066FF;
    --color-white: #FFFFFF;
    --color-light-gray: #F5F5F5;
    --color-dark-gray: #333333;
    --color-error: #FF4444;
    --color-success: #00CC00;
}

/* 3. Typography Base */
html { font-size: 16px; }
body {
    font-family: system fonts;
    color: var(--color-dark-gray);
    line-height: 1.6;
    background-color: var(--color-white);
}

h1, h2, h3, h4 { margin-bottom: 16px; font-weight: 700; }
h1 { font-size: 32px; }
h2 { font-size: 28px; }
h3 { font-size: 22px; }
h4 { font-size: 18px; }

/* 4. Utility Classes */
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.text-center { text-align: center; }
.mt { margin-top: 24px; }
.mb { margin-bottom: 24px; }
```

**header.css (~150 lines):**
```css
.header {
    position: sticky;
    top: 0;
    z-index: 1000;
    background-color: var(--color-primary);
    color: var(--color-white);
    height: 64px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    height: 100%;
}

.logo-section {
    display: flex;
    align-items: center;
    gap: 12px;
}

.nav-menu {
    display: flex;
    gap: 32px;
}

.nav-link {
    color: var(--color-white);
    text-decoration: none;
}

.nav-link:hover {
    text-decoration: underline;
}

.hamburger {
    display: none;
    flex-direction: column;
    background: none;
    border: none;
    cursor: pointer;
}

@media (max-width: 767px) {
    .nav-menu { display: none; }
    .hamburger { display: flex; }
}
```

**footer.css (~150 lines):**
```css
.footer {
    background-color: var(--color-primary);
    color: var(--color-white);
    padding: 48px 24px 24px;
    margin-top: auto;
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
    max-width: 1200px;
    margin: 0 auto 24px;
}

.footer-column h3 {
    margin-bottom: 16px;
    font-size: 18px;
}

.footer-column ul {
    list-style: none;
}

.footer-column li {
    margin-bottom: 8px;
}

.footer-column a {
    color: var(--color-white);
    text-decoration: none;
}

.footer-column a:hover {
    text-decoration: underline;
}

@media (max-width: 767px) {
    .footer-content { grid-template-columns: 1fr; }
}
```

**forms.css (~250 lines):**
```css
/* Input Fields */
input[type="text"],
input[type="email"],
input[type="password"],
input[type="file"],
textarea,
select {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: 16px;
    font-family: inherit;
}

input[type="file"] {
    display: none;
}

/* Buttons */
.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 200ms ease;
}

.btn-primary {
    background-color: var(--color-primary);
    color: var(--color-white);
}

.btn-primary:hover {
    background-color: #0052CC;
    box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
}

.btn-secondary {
    background-color: transparent;
    color: var(--color-white);
    border: 2px solid var(--color-white);
}

/* Drop Zone */
.drop-zone {
    border: 2px dashed var(--color-border);
    border-radius: 8px;
    padding: 48px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 200ms ease;
    min-height: 250px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.drop-zone:hover,
.drop-zone.dragover {
    border-color: var(--color-primary);
    background-color: #F0F4FF;
}

/* Error States */
input.error,
select.error {
    border-color: var(--color-error);
}

.error-message {
    color: var(--color-error);
    font-size: 14px;
    margin-top: 4px;
}
```

**cards.css (~100 lines):**
```css
.card {
    background-color: var(--color-light-gray);
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 200ms ease;
}

.card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    transform: scale(1.02);
}

.cards-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
}

.card-header {
    margin-bottom: 16px;
}

.card-body {
    margin-bottom: 16px;
    font-size: 14px;
    line-height: 1.6;
}

.card-footer {
    text-align: center;
}
```

**responsive.css (~350 lines):**
```css
/* Tablet (768px - 1023px) */
@media (max-width: 1023px) {
    .header-content { padding: 0 16px; }
    .container { padding: 0 16px; }
    .nav-menu { gap: 16px; }
}

/* Mobile (320px - 767px) */
@media (max-width: 767px) {
    html { font-size: 14px; }
    
    h1 { font-size: 24px; }
    h2 { font-size: 20px; }
    h3 { font-size: 18px; }
    
    .header { height: 56px; }
    .header-content { padding: 0 16px; }
    
    .nav-menu {
        position: absolute;
        top: 56px;
        left: 0;
        right: 0;
        background-color: var(--color-primary);
        flex-direction: column;
        gap: 0;
        padding: 16px 0;
        display: none;
    }
    
    .nav-menu.active { display: flex; }
    
    .btn-large {
        width: 100%;
        padding: 16px;
        min-height: 44px;
    }
    
    .drop-zone {
        min-height: 150px;
        padding: 24px 16px;
    }
    
    .cards-grid {
        grid-template-columns: 1fr;
        gap: 16px;
    }
    
    .footer-content { grid-template-columns: 1fr; }
    
    input, select, textarea {
        font-size: 16px; /* Prevents zoom on iOS */
        padding: 16px;
    }
}
```

---

## 9. Security Design

### 9.1 File Upload Validation

**Multi-Layer Validation:**

```python
def validate_upload(file, max_size=50*1024*1024):
    """Multi-layer file validation"""
    
    # 1. File presence check
    if not file or file.filename == '':
        return False, "No file selected"
    
    # 2. Extension check
    if not allowed_file(file.filename):
        return False, "Unsupported extension"
    
    # 3. File size check
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        return False, "File exceeds size limit"
    
    # 4. MIME type validation
    mime_type = file.content_type
    if not validate_mime_type(file.filename, mime_type):
        return False, "MIME type mismatch"
    
    # 5. File integrity check
    try:
        if file.filename.lower().endswith('.pdf'):
            # PDF integrity
            PDF(file)
        else:
            # Image integrity
            Image.open(file)
    except Exception:
        return False, "File is corrupted"
    
    return True, "Validation passed"
```

**Allowed Extensions & MIME Types:**

| Extension | MIME Type(s) |
|-----------|--------------|
| .jpg, .jpeg | image/jpeg |
| .png | image/png |
| .webp | image/webp |
| .bmp | image/bmp |
| .svg | image/svg+xml |
| .avif | image/avif |
| .jfif | image/jpeg |
| .gif | image/gif |
| .pdf | application/pdf |

### 9.2 Filename Sanitization

**Using secure_filename():**

```python
from werkzeug.utils import secure_filename

def save_upload(file, upload_folder):
    """Save file with sanitized filename"""
    # Sanitize original filename
    original_name = secure_filename(file.filename)
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    base_name, ext = os.path.splitext(original_name)
    unique_filename = f"{base_name}_{timestamp}{ext}"
    
    # Ensure path is within upload folder
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Verify path is safe
    if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
        raise ValueError("Path traversal attempt detected")
    
    file.save(file_path)
    return unique_filename
```

**Protection Against:**
- Special characters in filenames
- Path traversal attempts (../, ..\\)
- Unicode normalization attacks
- Null byte injection
- Reserved filenames (CON, PRN, AUX, etc.)

### 9.3 Path Traversal Prevention

**Defensive Practices:**

```python
import os

def safe_get_file(filename, base_folder):
    """Safely retrieve file path"""
    # Normalize paths
    base_abs = os.path.abspath(base_folder)
    file_abs = os.path.abspath(os.path.join(base_folder, filename))
    
    # Verify file is within base folder
    if not file_abs.startswith(base_abs):
        raise ValueError("Access denied")
    
    if not os.path.exists(file_abs):
        raise FileNotFoundError("File not found")
    
    return file_abs
```

**Implementation:**
- All file paths resolved through safe function
- No direct user input in file paths
- Absolute path comparison
- Folder containment verification

### 9.4 Temporary File Isolation

**Folder Structure:**
```
application/
├── images/           (Isolated folder, no web access)
├── converted_images/ (Isolated folder, no web access)
└── templates/        (Web accessible)
```

**Nginx Configuration (if applicable):**
```nginx
# Block direct access to upload folders
location ~ ^/(images|converted_images)/ {
    deny all;
}
```

**Access Control:**
- Files served only through Flask download handler
- No direct URL access to `/images/` or `/converted_images/`
- Download endpoint validates file ownership (if needed in future)

---

## 10. Accessibility Design

### 10.1 Semantic HTML Structure

**Proper HTML Hierarchy:**

```html
<!-- ✓ Correct -->
<header>
    <nav aria-label="Main navigation">
        <a href="/" aria-current="page">Home</a>
        <a href="/image-convert">Tools</a>
    </nav>
</header>

<main>
    <section aria-labelledby="section-title">
        <h1 id="section-title">Hero Section Title</h1>
    </section>
    
    <article>
        <h2>Article Title</h2>
        <p>Content...</p>
    </article>
</main>

<footer>
    <nav aria-label="Footer navigation">
        <!-- Footer links -->
    </nav>
</footer>

<!-- ✗ Incorrect -->
<div class="header">
    <div class="nav"><!-- Non-semantic divs --></div>
</div>
```

**Semantic Elements:**
- `<header>` for top section
- `<nav>` for navigation
- `<main>` for primary content
- `<section>` for logical sections
- `<article>` for independent content
- `<footer>` for footer
- `<form>`, `<fieldset>`, `<legend>` for forms
- `<ul>`, `<ol>`, `<li>` for lists

### 10.2 ARIA Labels Strategy

**Buttons & Controls:**
```html
<!-- Descriptive ARIA labels for icon buttons -->
<button class="hamburger" aria-label="Toggle navigation menu" aria-expanded="false">
    ☰
</button>

<!-- Drag-drop zone description -->
<div class="drop-zone" 
     role="region"
     aria-label="Drag and drop file upload zone"
     aria-describedby="zone-help">
    <p id="zone-help">Drag files here or click to browse</p>
</div>

<!-- Progress bar with aria-valuenow -->
<div class="progress-bar"
     role="progressbar"
     aria-valuenow="45"
     aria-valuemin="0"
     aria-valuemax="100"
     aria-label="File upload progress">
</div>

<!-- Live region for alerts -->
<div id="alerts" aria-live="polite" aria-atomic="true">
    <!-- Alert messages inserted here -->
</div>
```

**Form Elements:**
```html
<div class="form-group">
    <label for="formatSelect">Convert to:</label>
    <select id="formatSelect" name="format" aria-describedby="format-help" required>
        <option value="">-- Select Format --</option>
        <option value="PNG">PNG</option>
    </select>
    <small id="format-help">Choose your desired output format</small>
</div>

<input type="file" 
       id="imageInput" 
       name="file"
       aria-label="Select image file to upload"
       aria-describedby="file-help">
<small id="file-help">Supported formats: JPG, PNG, WebP, BMP</small>
```

### 10.3 Keyboard Navigation Patterns

**Tab Order:**
```html
<!-- Logical tab order following visual flow -->
<header>
    <a href="/" tabindex="1">Logo</a>
    <nav>
        <a href="/" tabindex="2">Home</a>
        <a href="/image-convert" tabindex="3">Image Tools</a>
    </nav>
    <button tabindex="4">Sign In</button>
    <button tabindex="5">Sign Up</button>
</header>

<main>
    <form>
        <input type="file" tabindex="10">
        <select tabindex="11"><!-- Format --></select>
        <button type="submit" tabindex="12">Upload</button>
    </form>
</main>
```

**Focus Indicators:**
```css
/* Visible focus indicator for all interactive elements */
button:focus,
a:focus,
input:focus,
select:focus {
    outline: 3px solid #0066FF;
    outline-offset: 2px;
}

/* Ensure focus is visible even on reduced-motion */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

**Keyboard Support:**
- Tab: Navigate forward through focusable elements
- Shift+Tab: Navigate backward
- Enter: Activate buttons, submit forms
- Space: Activate buttons, toggle checkboxes
- Escape: Close modals, dismiss alerts
- Arrow keys: Navigate dropdowns, menus

### 10.4 Focus Management

**Modal/Alert Dismissal:**
```javascript
// When alert is shown, trap focus within alert
function showAlert(message) {
    const alertEl = createAlert(message);
    alertEl.focus();
    
    // Trap focus in alert
    alertEl.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAlert();
            // Return focus to trigger element
            previouslyFocusedElement.focus();
        }
    });
}

// Restore focus after modal closes
function closeModal() {
    modal.remove();
    triggerButton.focus();
}
```

**Skip Navigation Link:**
```html
<a href="#main-content" class="skip-link">Skip to main content</a>

<main id="main-content">
    <!-- Page content -->
</main>

<style>
.skip-link {
    position: absolute;
    left: -9999px;
    z-index: 999;
}

.skip-link:focus {
    left: 0;
    top: 0;
}
</style>
```

---

## 11. Implementation Priority

### Phase 1: Backend Infrastructure (Days 1-3)
- Set up Flask routes: GET /, GET /image-convert, POST /image-convert, GET /pdf-to-word, POST /pdf-to-word
- Implement file upload validation (extension, size, MIME type)
- Create file handling utilities (sanitization, cleanup)
- Set up temporary file storage (images/, converted_images/)
- Implement error response structures
- Add logging infrastructure

### Phase 2: Image Conversion Engine (Days 4-6)
- Implement PIL-based image conversion
- Add format-specific handlers (transparency, SVG, AVIF)
- Implement quality settings (WebP 90%, JPG 85%)
- Add file cleanup mechanism (post-download + periodic)
- Test with various image formats
- Error handling and logging

### Phase 3: PDF Conversion Engine (Days 7-8)
- Integrate pdf2docx library
- Implement PDF validation and protection detection
- Add multi-page PDF handling
- Test conversion with various PDFs
- Error handling for protected/corrupted PDFs

### Phase 4: Frontend Templates (Days 9-11)
- Create base.html with header/footer
- Build index.html with hero + card grid
- Create image_converter.html with drag-drop zone
- Create pdf_converter.html with drag-drop zone
- Implement form structure and validation feedback
- Add semantic HTML and ARIA attributes

### Phase 5: CSS Styling (Days 12-14)
- Write main.css (base styles, typography)
- Write header.css (sticky header, nav)
- Write footer.css (multi-column layout)
- Write forms.css (inputs, buttons, drop zones)
- Write cards.css (grid layout, hover effects)
- Write responsive.css (mobile, tablet, desktop)
- Test responsive design across breakpoints

### Phase 6: JavaScript Interactivity (Days 15-17)
- Implement drag-and-drop functionality
- Add file preview and size display
- Create upload progress bar
- Add form validation feedback
- Implement success/error alert components
- Add keyboard navigation enhancements
- Mobile hamburger menu toggle

### Phase 7: Accessibility & Polish (Days 18-19)
- Add ARIA labels and descriptions
- Verify keyboard navigation
- Test with screen reader (NVDA, JAWS)
- Ensure focus indicators visible
- Fix color contrast issues
- Test across browsers (Chrome, Firefox, Safari, Edge)

### Phase 8: Testing & Refinement (Day 20)
- Unit tests for conversion functions
- Integration tests for routes
- Manual testing across devices
- Performance testing
- Security review
- Bug fixes and refinements

---

## 12. Correctness Properties

*Properties represent universal characteristics that should hold true across all valid executions of the system. They bridge human-readable specifications with machine-verifiable correctness guarantees.*

### Property 1: File Extension Validation

**For any** uploaded file with an invalid extension (not in JPG, JPEG, PNG, WebP, JFIF, BMP, SVG, AVIF for images; not PDF for PDFs), the system SHALL reject it with HTTP 400 and the appropriate error message.

**Validates: Requirements 1.2, 5.2**

---

### Property 2: File Size Enforcement

**For any** uploaded file exceeding 50MB in size, the system SHALL reject it with HTTP 400 and return the error message "File size exceeds 50MB limit."

**Validates: Requirements 1.4, 5.3**

---

### Property 3: MIME Type Verification

**For any** uploaded file, if the MIME type does not match the file extension, the system SHALL reject it and return an error response.

**Validates: Requirements 1.5, 25.5, 25.6**

---

### Property 4: Image Format Conversion Round-Trip

**For any** valid image file in a supported input format, converting it to an output format and reading the result SHALL produce a valid image with the correct target format.

**Validates: Requirements 2.2, 3.1, 3.2**

---

### Property 5: PNG to JPG Transparency Handling

**For any** PNG image with transparency (RGBA mode) converted to JPG, the resulting JPG SHALL have a white background where transparency was present, with no transparency remaining.

**Validates: Requirements 3.3**

---

### Property 6: SVG Rasterization

**For any** SVG input file converted to a raster format, the output SHALL be a valid raster image with dimensions of 1024x1024 pixels.

**Validates: Requirements 2.5, 3.4**

---

### Property 7: WebP Quality Preservation

**For any** image converted to WebP format, the conversion SHALL use 90% quality compression level.

**Validates: Requirements 3.4**

---

### Property 8: JPG Quality Setting

**For any** image converted to JPG format, the conversion SHALL use 85% quality compression level.

**Validates: Requirements 3.3**

---

### Property 9: Filename Pattern Generation

**For any** converted image file, the generated filename SHALL follow the pattern `{original_basename}_{target_format}.{extension}`.

**Validates: Requirements 3.2**

---

### Property 10: Download Link Generation

**For any** successful image conversion, the response SHALL include a `download_url` field containing a valid download link to the converted file.

**Validates: Requirements 4.1, 4.2**

---

### Property 11: File Cleanup Post-Download

**For any** download operation that completes successfully, both the original uploaded file and the converted file SHALL be deleted from the server after the download response is sent.

**Validates: Requirements 4.2, 4.3**

---

### Property 12: Orphaned File Cleanup

**For any** temporary files in the `images/` or `converted_images/` folders older than 1 hour, the system SHALL delete them during the next cleanup cycle.

**Validates: Requirements 4.3, 4.5**

---

### Property 13: PDF Extension Acceptance

**For any** uploaded file with the `.pdf` extension (case-insensitive), the system SHALL accept it for PDF conversion processing.

**Validates: Requirements 5.1**

---

### Property 14: PDF Protection Detection

**For any** password-protected or encrypted PDF file, the system SHALL detect the protection and return the error message "PDF is password-protected. Please remove the protection and try again."

**Validates: Requirements 5.5, 6.4**

---

### Property 15: Multi-Page PDF Processing

**For any** PDF with multiple pages, the system SHALL convert all pages into a single DOCX file with page breaks preserved between original PDF pages.

**Validates: Requirements 6.1, 6.3**

---

### Property 16: PDF Conversion Performance

**For any** PDF file up to 100+ pages, the system SHALL complete conversion within 30 seconds.

**Validates: Requirements 6.2**

---

### Property 17: DOCX Filename Pattern

**For any** PDF converted to DOCX, the generated filename SHALL follow the pattern `{original_basename}.docx`.

**Validates: Requirements 7.3**

---

### Property 18: Header Sticky Behavior

**For any** page on the application, the header element SHALL maintain its position at the top of the viewport when scrolling, with `position: sticky` and `top: 0`.

**Validates: Requirements 8.1**

---

### Property 19: Header Navigation Links

**For any** active page, the corresponding navigation link in the header SHALL have `aria-current="page"` attribute.

**Validates: Requirements 8.3, 28.4**

---

### Property 20: Footer Multi-Column Layout

**For any** screen width of 1024px or greater (desktop), the footer SHALL display three columns: Product Links, Company Info, and Legal.

**Validates: Requirements 9.2, 9.3, 16.4**

---

### Property 21: Format Dropdown Validation

**For any** image conversion form submission without a selected format, the form SHALL not submit and SHALL display the inline error message "Please select a target format".

**Validates: Requirements 2.3**

---

### Property 22: Drag-and-Drop Hover Effect

**For any** drag event over the drop zone, the zone's background SHALL change to a lighter blue shade and display a blue border highlight.

**Validates: Requirements 11.7, 18.5**

---

### Property 23: Progress Bar Percentage Display

**For any** file upload in progress, the progress bar WIDTH and percentage TEXT SHALL accurately reflect the upload progress (0-100%), updated in real-time.

**Validates: Requirements 11.8, 12.7**

---

### Property 24: Error Alert Display

**For any** error response from the backend, the frontend SHALL display an error alert at the top of the page with the error message and a dismissible close button.

**Validates: Requirements 13.1, 13.2**

---

### Property 25: Success Message Display

**For any** successful file conversion, the frontend SHALL display the success message "Conversion successful! Your file is ready for download" with a prominent Download button.

**Validates: Requirements 13.3, 13.4**

---

### Property 26: Mobile Responsive Layout

**For any** screen width between 320px and 767px, the frontend SHALL display elements in a single-column vertical stack layout.

**Validates: Requirements 14.1**

---

### Property 27: Mobile Hamburger Menu

**For any** screen width less than 768px, the navigation menu SHALL be hidden by default and only displayed when the hamburger menu is toggled.

**Validates: Requirements 8.5, 14.2**

---

### Property 28: Touch Target Minimum Size

**For any** interactive element (button, link, input) on mobile (320px-767px), the minimum height and width SHALL be 44px to facilitate touch interaction.

**Validates: Requirements 14.4**

---

### Property 29: Mobile Minimum Font Size

**For any** text content on mobile (320px-767px), the font size SHALL be at least 16px to prevent automatic zoom on iOS.

**Validates: Requirements 14.5**

---

### Property 30: Tablet Two-Column Layout

**For any** screen width between 768px and 1023px (tablet), the home page card grid SHALL display in a two-column layout.

**Validates: Requirements 15.1**

---

### Property 31: Primary Color Consistency

**For any** header, footer, button, or primary UI element, the background or accent color SHALL be the vibrant blue (#0066FF) or a shade derivative.

**Validates: Requirements 8.6, 9.6, 17.1**

---

### Property 32: Text Color Contrast

**For any** body text (14-16px), the contrast ratio between text color (#333333) and background (#FFFFFF) SHALL be at least 4.5:1 for WCAG AA compliance.

**Validates: Requirements 17.3, 17.4**

---

### Property 33: Link Underline on Hover

**For any** hyperlink in the navigation, hovering SHALL underline the link text and change color to a darker shade of blue.

**Validates: Requirements 18.2**

---

### Property 34: Button Click Visual Feedback

**For any** button click interaction, the button SHALL display brief visual feedback (color change or scale reduction) for approximately 100ms.

**Validates: Requirements 18.4**

---

### Property 35: Card Hover Scale Effect

**For any** card hover interaction, the card SHALL scale by 2% in size and increase shadow depth.

**Validates: Requirements 10.7, 18.3**

---

### Property 36: Static CSS File Organization

**The frontend CSS** SHALL be organized into six modular files: main.css, header.css, footer.css, forms.css, cards.css, responsive.css, stored in static/css/.

**Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7**

---

### Property 37: Filename Sanitization

**For any** uploaded file, the filename SHALL be sanitized using `secure_filename()` or equivalent, removing special characters and preventing path traversal attempts.

**Validates: Requirements 25.1, 25.3**

---

### Property 38: Image Conversion Performance

**For any** valid image file (up to 10MB), the conversion SHALL complete within 10 seconds.

**Validates: Requirements 3.1, 26.1, 26.2**

---

### Property 39: Semantic HTML Structure

**All page templates** SHALL use semantic HTML elements: header, nav, main, section, footer, article, aside, form, fieldset, label, ul/ol/li.

**Validates: Requirements 27.1, 27.2, 27.3, 27.4**

---

### Property 40: ARIA Labels for Buttons

**For any** interactive button element, there SHALL be a descriptive `aria-label` attribute or associated text describing its purpose.

**Validates: Requirements 28.1**

---

### Property 41: Tab Navigation

**For any** page, all interactive elements SHALL be reachable and navigable using only the Tab key in a logical order matching visual flow.

**Validates: Requirements 29.1, 29.2**

---

### Property 42: Focus Indicator Visibility

**For any** focusable element receiving keyboard focus, a visible focus indicator (outline or ring) SHALL be displayed with minimum 3px width and sufficient contrast.

**Validates: Requirements 29.2**

---

### Property 43: Enter Key Button Activation

**For any** button element, pressing the Enter or Space key while focused SHALL activate the button's action.

**Validates: Requirements 29.3**

---

### Property 44: Escape Key Alert Dismissal

**For any** error or success alert on screen, pressing the Escape key SHALL dismiss the alert from the page.

**Validates: Requirements 29.4, 13.2**

---

### Property 45: Browser Compatibility

**The frontend** SHALL render without critical errors on Chrome 90+, Firefox 88+, Safari 14+, and Edge 90+.

**Validates: Requirements 30.1, 30.2, 30.3, 30.4**

---

