document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const urlForm = document.getElementById('urlForm');
    const urlInput = document.getElementById('urlInput');
    const scanButton = document.getElementById('scanButton');
    const resultContainer = document.getElementById('resultContainer');
    const threatBadge = document.getElementById('threatBadge');
    const threatIcon = document.getElementById('threatIcon');
    const threatText = document.getElementById('threatText');
    const threatMeter = document.getElementById('threatMeter');
    const aiAnalysis = document.getElementById('aiAnalysis');
    const exportButton = document.getElementById('exportButton');
    const modelSelection = document.getElementById('modelSelection');
    
    // Add a dark mode toggle icon
    const darkModeIcon = document.createElement('div');
    darkModeIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
    darkModeIcon.className = 'dark-mode-icon';
    darkModeIcon.style.cursor = 'pointer';
    darkModeIcon.style.position = 'fixed';
    darkModeIcon.style.top = '1rem';
    darkModeIcon.style.right = '1rem';
    darkModeIcon.style.zIndex = '1000';
    document.body.appendChild(darkModeIcon);

    // Toggle dark mode on icon click
    darkModeIcon.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });

    // Apply dark mode based on user preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }

    // Form submission handler
    urlForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const url = urlInput.value;
        const useAttention = modelSelection.value === "attention";

        // Show scanning animation
        scanButton.querySelector('.button-text').textContent = 'Scanning...';
        scanButton.querySelector('.spinner').classList.remove('hidden');
        scanButton.disabled = true;

        fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                use_attention: useAttention
            })
        })
        .then(response => response.json())
        .then(data => {
            // Update threat indicators
            updateThreatIndicators(data.classification, data.threat_level);

            // Update AI analysis
            aiAnalysis.innerHTML = `<p>${data.analysis}</p>`;

            // Show result container
            resultContainer.classList.remove("hidden");
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while scanning the URL.');
        })
        .finally(() => {
            // Reset button state
            scanButton.querySelector('.button-text').textContent = 'Check URL Now';
            scanButton.querySelector('.spinner').classList.add('hidden');
            scanButton.disabled = false;
        });
    });

    // Model selection change handler
    modelSelection.addEventListener('change', function() {
        if (urlInput.value && !resultContainer.classList.contains("hidden")) {
            // Show loading animation for AI analysis
            aiAnalysis.innerHTML = '<div class="analysis-loading"><div class="dot-typing"></div></div>';
            
            // Trigger a new scan
            urlForm.dispatchEvent(new Event('submit'));
        }
    });

    // PDF handling function
    function handlePDFResponse(blob) {
        // Create blob URL
        const blobUrl = window.URL.createObjectURL(
            new Blob([blob], { type: 'application/pdf' })
        );
        
        // Function to fallback to download
        function downloadPDF() {
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = `threat_analysis_${Date.now()}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        // Try to detect PDF viewer support
        const isPDFSupported = navigator.mimeTypes['application/pdf'] !== undefined || 
                              (navigator.plugins && Array.from(navigator.plugins).some(p => p.name.indexOf('PDF') >= 0));
        
        if (isPDFSupported) {
            // Try to open in new tab first
            const newWindow = window.open(blobUrl, '_blank');
            
            // If blocked by popup blocker or failed, fallback to download
            if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
                downloadPDF();
            }
        } else {
            // Fallback to download for browsers without PDF support
            downloadPDF();
        }
        
        // Clean up blob URL after a delay
        setTimeout(() => {
            window.URL.revokeObjectURL(blobUrl);
        }, 1000);
    }

    // Export button handler
    document.getElementById('exportButton').addEventListener('click', function() {
        const url = document.getElementById("urlInput").value;
        const useAttention = document.getElementById("modelSelection").value === "attention";
        
        // Show loading state
        this.disabled = true;
        const originalContent = this.innerHTML;
        this.innerHTML = '<div class="spinner"></div><span>Generating PDF...</span>';
        
        fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                use_attention: useAttention,
                format: 'pdf'
            })
        })
        .then(response => {
            if (!response.ok) throw new Error('PDF generation failed');
            return response.blob();
        })
        .then(handlePDFResponse)
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating the PDF report. Please try again.');
        })
        .finally(() => {
            // Reset button state
            this.disabled = false;
            this.innerHTML = originalContent;
        });
    });

    function updateThreatIndicators(classification, threatLevel) {
        // Update badge
        threatBadge.className = `badge ${classification}`;
        threatText.textContent = classification.charAt(0).toUpperCase() + classification.slice(1);

        // Map threat level to color
        const colors = {
            'benign': 'var(--safe-color)',
            'defacement': 'var(--neutral-color)',
            'phishing': 'var(--danger-color)',
            'malware': 'var(--danger-color)'
        };
        
        // Update meter width (0-3 scale)
        const percentage = (threatLevel / 3) * 100;
        threatMeter.style.width = `${percentage}%`;
        threatMeter.style.backgroundColor = colors[classification] || colors['benign'];
    }
});