# Implementation Plan: Image Processing Toolkit MVP

## Overview

This implementation plan breaks down the Image Processing Toolkit MVP into 40 executable tasks across 8 categories. Tasks are sequenced to build incrementally from infrastructure → backend → processing engines → frontend templates → styling → interactions → accessibility. Each task includes specific acceptance criteria and dependencies for parallel execution tracking.

---

## Phase 1: Infrastructure & Setup (5 tasks)

### ✓ 1.1 Update requirements.txt with dependencies
- **Description:** Add missing Python libraries (pdf2docx, Pillow updates, Flask extensions) to requirements.txt for image and PDF processing
- **Acceptance Criteria:**
  - pdf2docx>=0.5.13 added
  - Pillow>=9.3.0 confirmed
  - Flask==2.2.2 confirmed
  - File is saved and ready for pip install
- **Dependencies:** None
- **Effort:** 0.5 hours
- **Type:** infrastructure
- **Priority:** required
- **Implementation Notes:** Maintain existing Flask/Pillow versions, add pdf2docx only. Use exact versions to avoid conflicts.

### ✓ 1.2 Create project folder structure
- **Description:** Create static/css, static/js, utils/, templates/components directories and initialize __init__.py files where needed
- **Acceptance Criteria:**
  - Folder structure created: static/css/, static/js/, utils/, templates/components/
  - All Python modules have proper __init__.py
  - Directories are Git-tracked (no .gitkeep needed)
- **Dependencies:** 1.1
- **Effort:** 0.5 hours
- **Type:** infrastructure
- **Priority:** required
- **Implementation Notes:** Create empty __init__.py in utils/ for module imports. Use pathlib.Path for cross-platform compatibility.

### ✓ 1.3 Configure Flask app settings (main.py)
- **Description:** Set up Flask secret key, upload folder config, file size limits, and error handlers in main.py
- **Acceptance Criteria:**
  - Secret key configured (use os.urandom or environment variable)
  - MAX_CONTENT_LENGTH set to 50MB (52428800 bytes)
  - UPLOAD_FOLDER and CONVERTED_FOLDER configured
  - ALLOWED_IMAGE_EXTENSIONS defined: ['jpg', 'jpeg', 'png', 'webp', 'jfif', 'bmp', 'svg', 'avif']
  - ALLOWED_IMAGE_FORMATS defined: ['PNG', 'JPG', 'WebP', 'BMP']
- **Dependencies:** 1.2
- **Effort:** 1 hour
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Use app.config dictionary for all settings. Store constants at module level for reuse across routes and utilities.

### ✓ 1.4 Create file_handler.py utility module
- **Description:** Implement file validation, sanitization, and security checks in utils/file_handler.py
- **Acceptance Criteria:**
  - sanitize_filename() function using werkzeug.utils.secure_filename
  - validate_file_extension() checks against allowed extensions
  - validate_file_size() checks 50MB limit
  - validate_mime_type() checks MIME type matches extension
  - is_file_corrupted() attempts to open file with PIL/mimetypes
  - All functions return (success: bool, error_message: str) tuple
- **Dependencies:** 1.3
- **Effort:** 1.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Use werkzeug for MIME type detection. Import mimetypes module for fallback. All functions should be testable in isolation.

### ✓ 1.5 Create temporary file cleanup utility (utils/cleanup.py)
- **Description:** Implement cleanup functions for orphaned files with timestamp-based deletion in utils/cleanup.py
- **Acceptance Criteria:**
  - cleanup_old_files(folder, max_age_hours) function deletes files older than max_age
  - Logs deleted file paths for monitoring
  - Handles permission errors gracefully
  - safe_remove_file() wraps os.remove with try-catch
  - 1-hour retention for completed conversions, 5-minute for aborts
- **Dependencies:** 1.4
- **Effort:** 1 hour
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Use os.path.getmtime() for file age calculation. Use app.logger for all cleanup events. Call on app startup.

---

## Phase 2: Backend Routes (6 tasks)

### ✓ 2.1 Implement GET / route (home page)
- **Description:** Create Flask route for home page that renders index.html with hero section and tool cards
- **Acceptance Criteria:**
  - Route handler returns render_template('index.html')
  - HTTP 200 status on success
  - No parameters required
  - Properly decorated with @app.route('/', methods=['GET'])
- **Dependencies:** 1.3
- **Effort:** 0.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Simple pass-through route. Add error handler for 500 errors that renders error.html.

### ✓ 2.2 Implement GET /image-convert route
- **Description:** Create Flask route that renders image_converter.html template
- **Acceptance Criteria:**
  - Route handler returns render_template('image_converter.html')
  - HTTP 200 status on success
  - Template receives allowed formats: ['PNG', 'JPG', 'WebP', 'BMP']
  - Properly decorated with @app.route('/image-convert', methods=['GET'])
- **Dependencies:** 1.3
- **Effort:** 0.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Pass `allowed_formats` to template context for dropdown population.

### ✓ 2.3 Implement POST /image-convert route (main handler)
- **Description:** Create Flask route that validates input, calls image processor, returns JSON response
- **Acceptance Criteria:**
  - Accepts multipart/form-data with 'file' and 'format' fields
  - Validates file presence, extension, size, MIME type using file_handler
  - Returns JSON with status, message, download_url, filename
  - Returns HTTP 400 for validation errors
  - Returns HTTP 200 for successful conversion
  - Returns HTTP 500 for processing errors
  - Logs all errors via app.logger
- **Dependencies:** 1.4, 1.5, 2.2
- **Effort:** 2 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Store uploaded file with sanitized name in `images/` folder. Call image_processor.convert_image(). Do NOT clean up files here—that's for download handler.

### ✓ 2.4 Implement GET /pdf-to-word route
- **Description:** Create Flask route that renders pdf_converter.html template
- **Acceptance Criteria:**
  - Route handler returns render_template('pdf_converter.html')
  - HTTP 200 status on success
  - Properly decorated with @app.route('/pdf-to-word', methods=['GET'])
- **Dependencies:** 1.3
- **Effort:** 0.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Simple pass-through like /image-convert.

### ✓ 2.5 Implement POST /pdf-to-word route (main handler)
- **Description:** Create Flask route that validates PDF input, calls pdf processor, returns JSON response
- **Acceptance Criteria:**
  - Accepts multipart/form-data with 'file' field
  - Validates file extension is .pdf (case-insensitive)
  - Validates file size <= 50MB
  - Validates MIME type is application/pdf
  - Checks for password protection before conversion
  - Returns JSON with status, message, download_url, filename
  - Returns HTTP 400 for validation errors
  - Returns HTTP 200 for successful conversion
  - Returns HTTP 500 for processing errors
- **Dependencies:** 1.4, 1.5, 2.4
- **Effort:** 2 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Store uploaded PDF with sanitized name. Call pdf_processor.convert_pdf(). Validate MIME type strictly as application/pdf.

### ✓ 2.6 Implement download routes (/converted_image/<filename>, /converted_document/<filename>)
- **Description:** Create Flask routes that serve converted files with cleanup on download complete
- **Acceptance Criteria:**
  - Image route: GET /converted_image/<filename> serves file from converted_images/
  - PDF route: GET /converted_document/<filename> serves file from converted_images/
  - Both validate filename doesn't contain path traversal attempts
  - Both use send_from_directory() for security
  - Both register cleanup callback via @response.call_on_close
  - Cleanup deletes both original upload and converted file
  - HTTP 404 if file not found
  - HTTP 200 with file content on success
- **Dependencies:** 2.3, 2.5
- **Effort:** 1.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Use secure_filename() to validate filename parameter. Use send_file() with as_attachment=True. Implement cleanup_after_download() helper.

---

## Phase 3: Image Processing Engine (6 tasks)

### ✓ 3.1 Create image_processor.py module with format validation
- **Description:** Create utils/image_processor.py with PIL-based image format validation and detection
- **Acceptance Criteria:**
  - is_valid_image() opens file with PIL and returns True if readable
  - get_image_dimensions() returns (width, height) tuple
  - get_image_format() returns detected PIL format string
  - All functions handle PIL exceptions gracefully
  - Returns (success, error_message) for error cases
- **Dependencies:** 1.4
- **Effort:** 1 hour
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Use PIL.Image.open() for all validation. Catch PIL.UnidentifiedImageError for corrupted files.

### ✓ 3.2 Implement basic image format conversion (PIL)
- **Description:** Implement convert_image() function in image_processor.py with support for PNG, JPG, WebP, BMP
- **Acceptance Criteria:**
  - convert_image(input_path, output_path, format) function signature
  - Supports PNG, JPG, WebP, BMP output formats
  - Returns (success: bool, error_message: str) tuple
  - Conversion completes within 10 seconds for 10MB file
  - Filename generated as {original_basename}_{format}.{ext}
  - Saves to converted_images/ folder
- **Dependencies:** 3.1
- **Effort:** 1.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Handle format names case-insensitively (user selects "PNG" but saves as "png" format string). Use PIL.Image.save() with appropriate format parameter.

### ✓ 3.3 Implement PNG-to-JPG transparency flattening
- **Description:** Implement transparency handling for PNG→JPG conversion with white background
- **Acceptance Criteria:**
  - Detects RGBA mode (transparency channel)
  - Creates white RGB background (255, 255, 255)
  - Pastes image with alpha mask onto background
  - Result JPG has no transparency artifacts
  - Handles already-opaque PNG correctly (no modification)
- **Dependencies:** 3.2
- **Effort:** 1 hour
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Called as sub-function from convert_image() when format is JPG and image is RGBA. Add logic before PIL save() call.

### ✓ 3.4 Implement SVG rasterization (SVG→PNG/JPG/WebP/BMP)
- **Description:** Implement SVG rendering to raster format with 1024x1024 default dimensions
- **Acceptance Criteria:**
  - Detects .svg extension on upload
  - Rasterizes SVG to PNG intermediate format at 1024x1024 pixels
  - Converts intermediate PNG to user-selected format
  - Handles missing SVG library gracefully (fallback error message)
  - Returns error if SVG is invalid
- **Dependencies:** 3.2
- **Effort:** 1.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Use cairosvg library if available, fallback to PIL's SVG support or error message. Default size 1024x1024. May require external system library (Cairo).

### ✓ 3.5 Implement AVIF decoding and conversion
- **Description:** Implement AVIF input file support with conversion to selected output format
- **Acceptance Criteria:**
  - Detects .avif extension on upload
  - Opens AVIF using PIL (9.1+ has native support)
  - Converts to selected output format (PNG, JPG, WebP, BMP)
  - Handles transparency in AVIF→JPG (flatten like PNG)
  - Returns error if PIL doesn't support AVIF
- **Dependencies:** 3.2, 3.3
- **Effort:** 1 hour
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** PIL 9.1+ has AVIF support built-in. If earlier version, return error message "AVIF not supported by PIL version".

### ✓ 3.6 Set image compression/quality parameters
- **Description:** Configure output quality settings for lossy formats (JPG, WebP) and lossless compression (PNG)
- **Acceptance Criteria:**
  - JPG: quality=85 (85% quality, good compression)
  - WebP: quality=90 (90% quality, modern compression)
  - PNG: compress_level=9 (maximum lossless compression)
  - BMP: no compression (uncompressed)
  - Settings applied in convert_image() save() calls
- **Dependencies:** 3.2
- **Effort:** 0.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Add as configuration constants. Pass as kwargs to image.save().

---

## Phase 4: PDF Processing Engine (4 tasks)

### ✓ 4.1 Create pdf_processor.py module with validation
- **Description:** Create utils/pdf_processor.py with PDF file validation using pdf2docx
- **Acceptance Criteria:**
  - validate_pdf() checks if file is valid PDF
  - detect_pdf_encryption() checks for password protection
  - get_pdf_page_count() returns number of pages
  - All functions return (success: bool, error_message: str)
  - Handles corrupted PDFs gracefully
- **Dependencies:** 1.4
- **Effort:** 1 hour
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Use pdf2docx.PDF class for validation. Import PyPDF2 for encryption detection if available.

### ✓ 4.2 Implement PDF-to-DOCX conversion
- **Description:** Implement convert_pdf_to_docx() using pdf2docx library for basic conversion
- **Acceptance Criteria:**
  - convert_pdf_to_docx(input_pdf, output_docx) function signature
  - Returns (success: bool, error_message: str) tuple
  - Processes multi-page PDFs (all pages in single DOCX)
  - Conversion completes within 30 seconds for 100+ page PDF
  - Filename generated as {original_basename}.docx
  - Saves to converted_images/ folder
- **Dependencies:** 4.1
- **Effort:** 1 hour
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Use pdf2docx.convert() function. Wrap in try-except to catch conversion errors. Test with sample multi-page PDF.

### ✓ 4.3 Implement multi-page PDF handling
- **Description:** Verify and log multi-page PDF processing with page break preservation
- **Acceptance Criteria:**
  - Page breaks preserved between original PDF pages in DOCX output
  - All pages included in output (no truncation)
  - Page count logged for monitoring
  - Tested with 50+ page PDF
- **Dependencies:** 4.2
- **Effort:** 0.5 hours
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** pdf2docx handles page breaks automatically. Add logging to verify page count before/after conversion.

### ✓ 4.4 Implement error handling for protected/corrupted PDFs
- **Description:** Add comprehensive error handling for password-protected and corrupted PDFs
- **Acceptance Criteria:**
  - Detects password-protected PDFs before conversion
  - Returns error: "PDF is password-protected. Please remove the protection and try again"
  - Detects corrupted PDFs and returns: "PDF file is corrupted or cannot be processed. Please upload a valid PDF"
  - Graceful handling of missing required libraries
  - All errors logged with stack trace
- **Dependencies:** 4.1
- **Effort:** 1 hour
- **Type:** backend
- **Priority:** required
- **Implementation Notes:** Check encryption status in POST handler before calling convert(). Catch all exceptions with specific error messages.

---

## Phase 5: Frontend Templates (6 tasks)

### ✓ 5.1 Refactor base.html template with header/footer includes
- **Description:** Create/refactor templates/base.html with CSS imports, header/footer includes, block structure
- **Acceptance Criteria:**
  - DOCTYPE, meta tags (charset, viewport, viewport-fit)
  - All CSS files imported: main.css, header.css, footer.css, forms.css, cards.css, responsive.css
  - All JS files imported: drag-drop.js, progress.js, ui-interactions.js
  - {% include 'components/header.html' %} at top
  - {% include 'components/footer.html' %} at bottom
  - {% block content %} for child templates
  - Message/alert flash handling
- **Dependencies:** 1.2
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use Jinja2 extends pattern. Import all CSS in <head>, all JS before </body>. Use url_for() for all static file paths.

### ✓ 5.2 Create header.html component with navigation
- **Description:** Create templates/components/header.html with sticky header, nav links, auth buttons, hamburger menu
- **Acceptance Criteria:**
  - Sticky header: position: sticky; top: 0;
  - Logo and title on left: "Image Processing Toolkit"
  - Navigation links center: Home, Image Tools, PDF Tools
  - Sign In / Sign Up buttons right (placeholder, no backend)
  - Hamburger menu hidden initially (shown on mobile via CSS)
  - All links have proper href attributes
  - aria-current="page" on active link
- **Dependencies:** 5.1
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use semantic <nav> element. Implement hamburger toggle via JavaScript click handler in ui-interactions.js.

### ✓ 5.3 Create footer.html component with multi-column layout
- **Description:** Create templates/components/footer.html with three columns: Product, Company, Legal
- **Acceptance Criteria:**
  - Three-column layout (desktop) / single-column (mobile) via CSS
  - Column 1 (Product): Image Converter, PDF Converter, Feature Requests
  - Column 2 (Company): About Us, Contact, Blog
  - Column 3 (Legal): Privacy Policy, Terms of Service, Cookie Policy
  - Copyright text at bottom: "© 2024 Image Processing Toolkit. All rights reserved."
  - All links as anchor tags with href="#"
- **Dependencies:** 5.1
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use CSS Grid for multi-column layout. All links are placeholder (href="#"). Store in components/ subdirectory.

### ✓ 5.4 Create index.html home page template
- **Description:** Create templates/index.html with hero section and tool card grid
- **Acceptance Criteria:**
  - Hero section: "Process Your Images and Documents Online"
  - Hero subtitle: "Fast, simple, and secure conversion tools"
  - "Get Started" button in hero
  - Tool card grid: Image Converter card + PDF to Word card
  - Each card has icon (placeholder SVG), title, description, link button
  - Card grid 2-column desktop, 1-column mobile (via responsive.css)
- **Dependencies:** 5.1, 5.2, 5.3
- **Effort:** 1.5 hours
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Extends base.html. Use semantic <section> elements. Card links go to /image-convert and /pdf-to-word.

### ✓ 5.5 Create image_converter.html page with drag-drop form
- **Description:** Create templates/image_converter.html with drag-drop zone, format selector, progress bar
- **Acceptance Criteria:**
  - Page title: "Image Converter"
  - Subtitle: "Convert images to PNG, JPG, WebP, or BMP"
  - Drag-drop zone with upload icon and text
  - Hidden file input with accept="image/*"
  - Format dropdown with options: PNG (selected), JPG, WebP, BMP
  - File info display (name, size) - hidden initially
  - Progress bar - hidden initially
  - Upload button
  - Success/error alert containers - hidden initially
- **Dependencies:** 5.1, 5.2, 5.3
- **Effort:** 1.5 hours
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Extends base.html. Form id="imageForm" for JS targeting. Use IDs for all interactive elements.

### ✓ 5.6 Create pdf_converter.html page with drag-drop form
- **Description:** Create templates/pdf_converter.html with drag-drop zone, progress bar (PDF-only)
- **Acceptance Criteria:**
  - Page title: "PDF to Word Converter"
  - Subtitle: "Convert PDF documents to editable Word format"
  - Drag-drop zone with upload icon and text
  - Hidden file input with accept=".pdf,application/pdf"
  - File info display (name, size) - hidden initially
  - Progress bar - hidden initially
  - Upload button
  - Success/error alert containers - hidden initially
- **Dependencies:** 5.1, 5.2, 5.3
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Extends base.html. Form id="pdfForm". Similar layout to image_converter.html but no format selector.

---

## Phase 6: CSS Styling (6 tasks)

### ✓ 6.1 Create main.css - base styles and typography
- **Description:** Create static/css/main.css with color palette, typography, base element styles, utility classes
- **Acceptance Criteria:**
  - CSS Reset or normalize.css styles
  - Color variables: --primary-blue (#0066FF), --white (#FFFFFF), --light-gray (#F5F5F5), --dark-gray (#333333), --red (#FF4444), --green (#00CC00)
  - Typography: sans-serif font stack (Arial, Helvetica, system-ui)
  - Heading styles: H1 (28-32px), H2 (24-28px), H3 (18-22px)
  - Body text: 14-16px line-height 1.6
  - Utility classes: .container, .text-center, .mt-*, .mb-*, .p-*
  - 300-400 lines of CSS
- **Dependencies:** 5.1
- **Effort:** 2 hours
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use CSS variables for colors. Define base margins/padding scale (8px units). Include box-sizing: border-box reset.

### ✓ 6.2 Create header.css - sticky header and navigation styles
- **Description:** Create static/css/header.css with header positioning, nav menu, logo, hamburger toggle
- **Acceptance Criteria:**
  - Header: sticky positioning, top: 0, background: --primary-blue, color: white
  - Height: 64px desktop, 56px mobile
  - Logo and title on left (display: flex, align-items: center)
  - Navigation menu center (flex layout, list reset)
  - Auth buttons right (flex layout)
  - Hamburger menu: hidden desktop, visible mobile (display: none → display: block at breakpoint)
  - Z-index: 1000 (above content)
  - 150-200 lines of CSS
- **Dependencies:** 6.1, 5.2
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use flexbox for layout. Hamburger styling: 3 span bars with transitions. Logo width ~40px.

### ✓ 6.3 Create footer.css - multi-column footer layout
- **Description:** Create static/css/footer.css with footer grid, multi-column layout, link styles
- **Acceptance Criteria:**
  - Footer: background: --primary-blue, color: white, padding: 48px 24px
  - Multi-column grid: 3 columns desktop (CSS Grid), 1 column mobile
  - Column headers (H3) bold, 18px
  - Links: white, no underline, underline on hover
  - Bottom section: copyright text, centered
  - 150-200 lines of CSS
- **Dependencies:** 6.1, 5.3
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use CSS Grid for 3-column layout. Footer links in <a> tags. Position at bottom of page.

### ✓ 6.4 Create forms.css - input, button, drag-drop, error states
- **Description:** Create static/css/forms.css with form controls, buttons, drag-drop zone, error/success styling
- **Acceptance Criteria:**
  - Text inputs: border 1px solid --light-gray, padding 8px, border-radius 4px, focus: border --primary-blue
  - Selects/dropdowns: same styling as inputs, appearance reset
  - Buttons: primary (--primary-blue bg, white text), secondary (--light-gray bg, dark text)
  - Button hover: darker shade (darken by 10%), cursor pointer
  - Button active: slight scale down (scale 0.98)
  - Drag-drop zone: border 2px dashed --light-gray, padding 24px, text-align center, min-height 250px desktop/150px mobile
  - Drag-over state: border --primary-blue, background lighten(--primary-blue, 10%)
  - Error message: color --red, margin 8px 0
  - Success message: color --green
  - 200-300 lines of CSS
- **Dependencies:** 6.1
- **Effort:** 1.5 hours
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use :focus-visible for keyboard nav focus indicators. Implement all button states. Drag-drop zone styling crucial for UX.

### ✓ 6.5 Create cards.css - card grid, hover effects, shadows
- **Description:** Create static/css/cards.css with card component, grid layout, hover animations
- **Acceptance Criteria:**
  - Card: background --light-gray, border-radius 8px, box-shadow 0 2px 8px rgba(0,0,0,0.1)
  - Card grid: 2 columns desktop, 1 column mobile (CSS Grid)
  - Card header: padding 16px, background optional
  - Card body: padding 16px
  - Card footer: padding 16px, border-top 1px solid lighter
  - Hover effects: shadow increase (0 4px 16px rgba(0,0,0,0.15)), scale 1.02
  - Transition: all 200ms ease-out
  - 100-150 lines of CSS
- **Dependencies:** 6.1
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use CSS Grid for card grid. Card border-radius 8px. Hover scale with transform. Smooth transitions on all hover effects.

### ✓ 6.6 Create responsive.css - media queries for mobile/tablet/desktop
- **Description:** Create static/css/responsive.css with all responsive breakpoints and overrides
- **Acceptance Criteria:**
  - Mobile (320-767px): stack all, hamburger menu visible, single column cards, drag-drop 150px height, buttons 44px min-height, font 16px min
  - Tablet (768-1023px): 2-column cards, inline nav, drag-drop 200px height
  - Desktop (1024px+): all inline, 3-column footer, drag-drop 250px height, full feature UI
  - All framework styles overridden at breakpoints
  - 300-400 lines of CSS
- **Dependencies:** 6.1-6.5
- **Effort:** 1.5 hours
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Mobile-first approach preferred but not required. Use @media (min-width: XXXpx) { }. Test on actual mobile devices. Breakpoints: 768px, 1024px.

---

## Phase 7: JavaScript Interactivity (4 tasks)

### ✓ 7.1 Create drag-drop.js - file upload and validation
- **Description:** Create static/js/drag-drop.js with drag-and-drop events, file selection, client-side validation
- **Acceptance Criteria:**
  - dragover event: add class "drag-over" (blue border, light bg)
  - dragleave event: remove "drag-over" class
  - drop event: get files from event.dataTransfer, validate, display file info
  - File input change: validate selected file
  - Validation: extension check, size check (50MB), display error if invalid
  - Display file name and size when valid: "photo.jpg - 2.5 MB"
  - Prevent default form submission until format selected
  - Target elements: #imageForm, #dropZone, #imageInput, #pdfForm (for PDF page)
- **Dependencies:** 5.5, 5.6
- **Effort:** 1.5 hours
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Vanilla JavaScript (no jQuery). Use event.preventDefault() to prevent browser default drag behavior. File size validation: file.size / (1024*1024) > 50. Add error messages to #imageForm.

### ✓ 7.2 Create progress.js - upload progress tracking
- **Description:** Create static/js/progress.js with XMLHttpRequest upload progress bar updates
- **Acceptance Criteria:**
  - Form submission: use XMLHttpRequest instead of default form submission
  - xhr.upload.addEventListener('progress', ...) to track bytes
  - Calculate percentage: (event.loaded / event.total) * 100
  - Update #progressFill width: style.width = percentage + '%'
  - Update #progressText: display "45%" etc.
  - Progress bar 0%: gray, 1-99%: blue gradient, 100%: green
  - On completion: show success message with download link
  - On error: show error message
- **Dependencies:** 7.1
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use XMLHttpRequest, not fetch (for upload progress support). Parse JSON response to get download_url. Handle network errors gracefully.

### ✓ 7.3 Create ui-interactions.js - alerts, focus management, micro-interactions
- **Description:** Create static/js/ui-interactions.js with alert dismissal, hamburger menu toggle, button interactions
- **Acceptance Criteria:**
  - Alert dismiss: click close button removes alert from DOM
  - Hamburger menu: click toggles nav menu visibility (add/remove class)
  - Button click: add "active" class for 100ms feedback
  - Error alert auto-dismiss after 5 seconds (optional)
  - Focus management: Tab key navigation through focusable elements
  - Escape key: dismiss open alerts/modals
  - All events delegated or attached to specific IDs/classes
- **Dependencies:** 5.2
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Vanilla JavaScript event listeners. Use classList.add/remove/toggle. Implement focus trap if modals added later.

### ✓ 7.4 Implement form submission handlers for image and PDF conversion
- **Description:** Wire up form submission handlers to POST routes with response handling
- **Acceptance Criteria:**
  - #imageForm submit: POST to /image-convert with file + format
  - #pdfForm submit: POST to /pdf-to-word with file
  - Show progress bar on submit
  - Parse JSON response (status, message, download_url, filename)
  - On success: display download link in success alert
  - On error: display error message in error alert
  - Disable submit button during upload
  - Re-enable button on completion or error
- **Dependencies:** 7.1, 7.2, 7.3
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use XMLHttpRequest or fetch with headers. Append FormData with file + format. Handle 400/500 responses. Store download_url for later use.

---

## Phase 8: Accessibility & Refinement (4 tasks)

### ✓ 8.1 Implement semantic HTML and ARIA labels
- **Description:** Add semantic HTML elements and ARIA attributes across all templates for assistive technology support
- **Acceptance Criteria:**
  - All templates use semantic elements: <header>, <nav>, <main>, <section>, <footer>, <article>, <form>
  - Heading hierarchy correct (no skipped levels)
  - All form inputs have associated <label> tags
  - All buttons have descriptive text or aria-label
  - Drag-drop zone has aria-label: "File upload drop zone"
  - Progress bar has aria-live="polite" aria-label="Upload progress"
  - Alert divs have role="alert" aria-live="assertive" or aria-live="polite"
  - Active nav link has aria-current="page"
- **Dependencies:** 5.1-5.6
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Audit all templates for semantic structure. Add ARIA attributes to dynamic elements. Test with screen reader.

### ✓ 8.2 Implement keyboard navigation and focus management
- **Description:** Ensure all interactive elements are keyboard accessible with visible focus indicators
- **Acceptance Criteria:**
  - All buttons, links, inputs focusable via Tab key
  - Visible focus indicator (outline or highlight) on all focusable elements
  - Enter/Space activates buttons and submits forms
  - Escape dismisses alerts
  - Logical tab order follows visual page flow
  - Focus outline color matches primary blue, at least 2px width
  - Tested with keyboard only (no mouse)
- **Dependencies:** 6.4, 7.3
- **Effort:** 1 hour
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Add :focus-visible styles to all interactive elements. Use outline property (not border). Test tab order by inspecting DOM.

### ✓ 8.3 Test color contrast and WCAG compliance (manual)
- **Description:** Verify color contrast ratios meet WCAG AA standards and test with accessibility tools
- **Acceptance Criteria:**
  - Text on primary blue (#0066FF) has sufficient contrast (test with WebAIM)
  - All text contrast ratio >= 4.5:1 for normal text, >= 3:1 for large text
  - Form error text (red) has sufficient contrast
  - No color-only conveyed information (text + icon for errors/success)
  - Tested with Chrome DevTools Lighthouse, Axe DevTools
  - Responsive design tested on mobile devices
- **Dependencies:** 6.1-6.6
- **Effort:** 1.5 hours
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use WebAIM Contrast Checker or Axe DevTools. Document any failures and fixes. Manual testing required—no automation.

### ✓ 8.4 Final testing and bug fixes
- **Description:** End-to-end testing of all features, bug fixes, performance optimization
- **Acceptance Criteria:**
  - Image conversion E2E: upload image → select format → convert → download works
  - PDF conversion E2E: upload PDF → convert → download works
  - Error handling: invalid file types show error, large files rejected
  - Responsive design: tested on mobile (375px), tablet (768px), desktop (1024px)
  - All buttons/forms functional
  - No JavaScript errors in console
  - Page load time < 2 seconds
  - Browser compatibility: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Dependencies:** All prior tasks
- **Effort:** 2 hours
- **Type:** frontend
- **Priority:** required
- **Implementation Notes:** Use browser DevTools to check console for errors. Test actual file conversions. Use real 50MB+ file to verify size limit. Document any remaining issues.

---

## Checkpoint Tasks

### ✓ Checkpoint 1: Backend Infrastructure Complete
- Ensure requirements.txt updated, Flask configured, all utility modules created and tested
- All file handler functions callable with expected signatures
- Cleanup utility can remove files by age
- Ask user if any questions arise with backend setup

### ✓ Checkpoint 2: Routes Implemented
- All 6 routes (GET /, GET /image-convert, POST /image-convert, GET /pdf-to-word, POST /pdf-to-word, download routes) callable
- Routes return expected JSON responses
- Error handling works (400 on validation error, 500 on exception)
- Ensure all tests pass, ask the user if questions arise.

### ✓ Checkpoint 3: Processing Engines Functional
- Image processor converts valid images to all output formats
- PDF processor converts valid PDFs to DOCX
- Transparency handling works (PNG→JPG)
- SVG rasterization works (or returns error if library missing)
- Ensure all tests pass, ask the user if questions arise.

### ✓ Checkpoint 4: Frontend Templates and Styling Complete
- All 6 templates render without errors
- Responsive design verified on 3+ screen sizes
- CSS properly organized in 6 files
- All links and buttons functional
- Ensure all tests pass, ask the user if questions arise.

### ✓ Checkpoint 5: JavaScript Interactivity Complete
- Drag-drop zone responds to drag events
- File validation works (extension, size)
- Progress bar shows during upload
- Forms submit via XMLHttpRequest
- Alerts display and dismiss correctly
- Ensure all tests pass, ask the user if questions arise.

### ✓ Checkpoint 6: Accessibility and Final Polish
- Keyboard navigation works (Tab through all elements)
- ARIA labels present on dynamic elements
- Color contrast verified
- No console errors
- All 3 E2E conversions (image→image, image→image, PDF→DOCX) work end-to-end
- Ensure all tests pass, ask the user if questions arise.

---

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1.1", "1.2"]
    },
    {
      "id": 1,
      "tasks": ["1.3", "1.4"]
    },
    {
      "id": 2,
      "tasks": ["1.5", "3.1", "4.1"]
    },
    {
      "id": 3,
      "tasks": ["2.1", "2.2", "2.4"]
    },
    {
      "id": 4,
      "tasks": ["2.3", "2.5"]
    },
    {
      "id": 5,
      "tasks": ["2.6", "3.2", "4.2"]
    },
    {
      "id": 6,
      "tasks": ["3.3", "3.4", "3.5", "3.6", "4.3", "4.4"]
    },
    {
      "id": 7,
      "tasks": ["5.1", "5.2", "5.3"]
    },
    {
      "id": 8,
      "tasks": ["5.4", "5.5", "5.6"]
    },
    {
      "id": 9,
      "tasks": ["6.1", "6.2", "6.3", "6.4", "6.5"]
    },
    {
      "id": 10,
      "tasks": ["6.6"]
    },
    {
      "id": 11,
      "tasks": ["7.1", "7.2"]
    },
    {
      "id": 12,
      "tasks": ["7.3", "7.4"]
    },
    {
      "id": 13,
      "tasks": ["8.1", "8.2"]
    },
    {
      "id": 14,
      "tasks": ["8.3", "8.4"]
    }
  ]
}
```

---

## Implementation Notes

### General Guidelines
- Each task builds on prior tasks; complete checkpoints before moving to next phase
- Use Python logging throughout backend (app.logger.info, app.logger.error)
- All routes should return JSON responses with status, message fields
- Use werkzeug security functions (secure_filename) everywhere
- Test each feature with actual files before considering complete
- Document any deviations from design in commit messages

### Backend Patterns
- All file validation functions return (success: bool, error_msg: str) tuples
- All conversions save to appropriate folder (images/ or converted_images/)
- All errors logged with stack traces
- Use try-catch-finally for file cleanup
- Delete both original + converted files after download

### Frontend Patterns
- Vanilla JavaScript only (no jQuery, no frameworks)
- All CSS organized in separate files by concern
- Template inheritance from base.html
- Use semantic HTML5 elements throughout
- ARIA labels on all dynamic content
- Focus states visible for all interactive elements

### Quality Standards
- No console errors or warnings
- All forms validate before submission
- All error messages user-friendly (no stack traces shown)
- All buttons have hover/active states
- All pages responsive to 320px, 768px, 1024px+ viewports
- Conversion completes within stated timeframes (10s image, 30s PDF)

