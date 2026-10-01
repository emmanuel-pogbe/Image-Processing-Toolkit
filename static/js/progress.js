/*
   Upload Progress Tracking
   Handles XMLHttpRequest progress events and progress bar updates
*/

(function() {
    'use strict';

    // Image Converter
    const imageForm = document.getElementById('imageForm');
    if (imageForm) {
        initializeImageFormHandler();
    }

    // PDF Converter
    const pdfForm = document.getElementById('pdfForm');
    if (pdfForm) {
        initializePDFFormHandler();
    }

    function initializeImageFormHandler() {
        const form = document.getElementById('imageForm');
        const fileInput = document.getElementById('imageInput');
        const formatSelect = document.getElementById('formatSelect');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const successScreen = document.getElementById('successScreen');
        const errorAlert = document.getElementById('errorAlert');
        const downloadLink = document.getElementById('downloadLink');
        const backBtn = document.getElementById('backBtn');
        const successTitle = document.getElementById('successTitle');

        if (!form) return;

        // Back button handler
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                resetForm();
            });
        }

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Validate format selected
            if (!formatSelect.value) {
                showError('Please select a target format');
                return;
            }

            // Validate file selected
            if (!fileInput.files || fileInput.files.length === 0) {
                showError('Please select an image file');
                return;
            }

            // Prepare form data
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('format', formatSelect.value);

            // Show progress bar
            progressContainer.style.display = 'block';
            successScreen.style.display = 'none';
            errorAlert.style.display = 'none';
            progressFill.classList.remove('complete', 'error');
            progressFill.style.width = '0%';
            progressText.textContent = '0%';

            // Create XMLHttpRequest for upload tracking
            const xhr = new XMLHttpRequest();

            // Track upload progress
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressFill.style.width = percentComplete + '%';
                    progressText.textContent = Math.round(percentComplete) + '%';
                }
            });

            // Handle completion
            xhr.addEventListener('loadend', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.status === 'success') {
                            progressFill.classList.add('complete');
                            progressFill.style.width = '100%';
                            progressText.textContent = '100%';
                            showSuccess(response.filename, response.format);
                        } else {
                            progressFill.classList.add('error');
                            showError(response.message);
                        }
                    } catch (err) {
                        progressFill.classList.add('error');
                        showError('An error occurred. Please try again.');
                    }
                } else {
                    progressFill.classList.add('error');
                    showError('Upload failed. Please try again.');
                }
            });

            // Handle network errors
            xhr.addEventListener('error', () => {
                progressFill.classList.add('error');
                showError('Network error. Please check your connection and try again.');
            });

            // Send request
            xhr.open('POST', '/image-convert');
            xhr.send(formData);
        });

        function showSuccess(filename, format) {
            // Hide progress and form
            progressContainer.style.display = 'none';
            form.style.display = 'none';
            
            // Update success title
            successTitle.textContent = 'Your images have been converted!';
            
            // After upload, initiate conversion
            setTimeout(() => {
                // In a real implementation, this would call the conversion endpoint
                // For now, we'll use the legacy converted_image route
                const baseFileName = filename.split('.')[0];
                const extension = format.toLowerCase();
                const downloadFileName = `${baseFileName}_${format}.${extension}`;
                
                downloadLink.href = `/converted_image/${downloadFileName}`;
                successScreen.style.display = 'flex';
                
                // Scroll to top
                window.scrollTo(0, 0);
            }, 500);
        }

        function showError(message) {
            const errorAlertText = document.getElementById('errorAlertText');
            errorAlertText.textContent = message;
            errorAlert.style.display = 'block';
            progressContainer.style.display = 'none';
        }

        function resetForm() {
            // Hide success screen and show form
            successScreen.style.display = 'none';
            form.style.display = 'block';
            
            // Reset form fields
            form.reset();
            progressContainer.style.display = 'none';
            errorAlert.style.display = 'none';
            document.getElementById('fileInfo').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'none';
            
            // Scroll to top
            window.scrollTo(0, 0);
        }
    }

    function initializePDFFormHandler() {
        const form = document.getElementById('pdfForm');
        const fileInput = document.getElementById('pdfInput');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const successScreen = document.getElementById('successScreen');
        const errorAlert = document.getElementById('errorAlert');
        const downloadLink = document.getElementById('downloadLink');
        const backBtn = document.getElementById('backBtn');
        const successTitle = document.getElementById('successTitle');

        if (!form) return;

        // Back button handler
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                resetForm();
            });
        }

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Validate file selected
            if (!fileInput.files || fileInput.files.length === 0) {
                showError('Please select a PDF file');
                return;
            }

            // Prepare form data
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            // Show progress bar
            progressContainer.style.display = 'block';
            successScreen.style.display = 'none';
            errorAlert.style.display = 'none';
            progressFill.classList.remove('complete', 'error');
            progressFill.style.width = '0%';
            progressText.textContent = '0%';

            // Create XMLHttpRequest for upload tracking
            const xhr = new XMLHttpRequest();

            // Track upload progress
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressFill.style.width = percentComplete + '%';
                    progressText.textContent = Math.round(percentComplete) + '%';
                }
            });

            // Handle completion
            xhr.addEventListener('loadend', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.status === 'success') {
                            progressFill.classList.add('complete');
                            progressFill.style.width = '100%';
                            progressText.textContent = '100%';
                            showSuccess(response.filename);
                        } else {
                            progressFill.classList.add('error');
                            showError(response.message);
                        }
                    } catch (err) {
                        progressFill.classList.add('error');
                        showError('An error occurred. Please try again.');
                    }
                } else {
                    progressFill.classList.add('error');
                    showError('Upload failed. Please try again.');
                }
            });

            // Handle network errors
            xhr.addEventListener('error', () => {
                progressFill.classList.add('error');
                showError('Network error. Please check your connection and try again.');
            });

            // Send request
            xhr.open('POST', '/pdf-to-word');
            xhr.send(formData);
        });

        function showSuccess(filename) {
            // Hide progress and form
            progressContainer.style.display = 'none';
            form.style.display = 'none';
            
            // Update success title
            successTitle.textContent = 'Your PDF has been converted!';
            
            // In a real implementation, this would be the DOCX download link
            const baseFileName = filename.split('.')[0];
            const downloadFileName = `${baseFileName}.docx`;
            
            downloadLink.href = `/converted_document/${downloadFileName}`;
            successScreen.style.display = 'flex';
            
            // Scroll to top
            window.scrollTo(0, 0);
        }

        function showError(message) {
            const errorAlertText = document.getElementById('errorAlertText');
            errorAlertText.textContent = message;
            errorAlert.style.display = 'block';
            progressContainer.style.display = 'none';
        }

        function resetForm() {
            // Hide success screen and show form
            successScreen.style.display = 'none';
            form.style.display = 'block';
            
            // Reset form fields
            form.reset();
            progressContainer.style.display = 'none';
            errorAlert.style.display = 'none';
            document.getElementById('fileInfo').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'none';
            
            // Scroll to top
            window.scrollTo(0, 0);
        }
    }
})();
