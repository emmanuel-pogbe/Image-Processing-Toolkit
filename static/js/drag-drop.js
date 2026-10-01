/*
   Drag-and-Drop File Upload Handler
   Handles file selection, validation, and drag-over states
*/

(function() {
    'use strict';

    // Image Converter Page
    const imageForm = document.getElementById('imageForm');
    if (imageForm) {
        initializeImageUpload();
    }

    // PDF Converter Page
    const pdfForm = document.getElementById('pdfForm');
    if (pdfForm) {
        initializePDFUpload();
    }

    function initializeImageUpload() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('imageInput');
        const formatSelect = document.getElementById('formatSelect');
        const fileInfo = document.getElementById('fileInfo');
        const errorMessage = document.getElementById('errorMessage');
        const uploadBtn = document.querySelector('#imageForm button[type="submit"]');

        if (!dropZone || !fileInput) return;

        // Drag over event
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('drag-over');
        });

        // Drag leave event
        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');
        });

        // Drop event
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelection(files[0], 'image');
            }
        });

        // Click to select
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0], 'image');
            }
        });

        // Keyboard support for drop zone
        dropZone.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInput.click();
            }
        });

        function handleFileSelection(file, type) {
            errorMessage.style.display = 'none';
            errorMessage.textContent = '';

            // File size validation (50MB)
            const maxSize = 50 * 1024 * 1024;
            if (file.size > maxSize) {
                showError('File exceeds the 50MB limit. Please select a smaller file');
                fileInput.value = '';
                fileInfo.style.display = 'none';
                return;
            }

            // Display file info
            const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = `${sizeInMB} MB`;
            fileInfo.style.display = 'block';
        }

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
        }
    }

    function initializePDFUpload() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('pdfInput');
        const fileInfo = document.getElementById('fileInfo');
        const errorMessage = document.getElementById('errorMessage');

        if (!dropZone || !fileInput) return;

        // Drag over event
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('drag-over');
        });

        // Drag leave event
        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');
        });

        // Drop event
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelection(files[0]);
            }
        });

        // Click to select
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });

        // Keyboard support
        dropZone.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInput.click();
            }
        });

        function handleFileSelection(file) {
            errorMessage.style.display = 'none';
            errorMessage.textContent = '';

            // Validate PDF extension
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                showError('Please select a valid PDF file');
                fileInput.value = '';
                fileInfo.style.display = 'none';
                return;
            }

            // File size validation (50MB)
            const maxSize = 50 * 1024 * 1024;
            if (file.size > maxSize) {
                showError('File exceeds the 50MB limit. Please select a smaller file');
                fileInput.value = '';
                fileInfo.style.display = 'none';
                return;
            }

            // Display file info
            const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = `${sizeInMB} MB`;
            fileInfo.style.display = 'block';
        }

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
        }
    }
})();
