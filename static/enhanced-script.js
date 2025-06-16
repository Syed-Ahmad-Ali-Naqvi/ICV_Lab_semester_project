(function () {
    // DOM elements
    const elements = {
        // File inputs
        image1: document.getElementById('image1'),
        image2: document.getElementById('image2'),

        // Containers
        imagePreviewContainer: document.getElementById('imagePreviewContainer'),
        image1Container: document.getElementById('image1Container'),
        image2Container: document.getElementById('image2Container'),

        // Analysis type
        singleAnalysis: document.getElementById('singleAnalysis'),
        compareAnalysis: document.getElementById('compareAnalysis'),
        singleMethodPanel: document.getElementById('singleMethodPanel'),
        compareMethodPanel: document.getElementById('compareMethodPanel'),

        // Method selection
        methodSelect: document.getElementById('methodSelect'),
        methodCheckboxes: document.getElementById('methodCheckboxes'),

        // Buttons
        analyzeBtn: document.getElementById('analyzeBtn'),
        clearBtn: document.getElementById('clearBtn'),
        analyzeSpinner: document.getElementById('analyzeSpinner'),

        // Results
        resultContainer: document.getElementById('resultContainer'),
        singleResult: document.getElementById('singleResult'),
        comparisonResult: document.getElementById('comparisonResult'),
        resultImage: document.getElementById('resultImage'),
        comparisonImage: document.getElementById('comparisonImage'),
        emptyResult: document.getElementById('emptyResult'),
        loadingOverlay: document.getElementById('loadingOverlay'),

        // Metrics
        metricsContainer: document.getElementById('metricsContainer'),
        singleMetrics: document.getElementById('singleMetrics'),
        comparisonMetrics: document.getElementById('comparisonMetrics'),
        emptyMetrics: document.getElementById('emptyMetrics'),
        executionTime: document.getElementById('executionTime'),
        meanMagnitude: document.getElementById('meanMagnitude'),
        maxMagnitude: document.getElementById('maxMagnitude'),
        methodsList: document.getElementById('methodsList'),
        timeChart: document.getElementById('timeChart')
    };

    // State
    let availableMethods = {};
    let currentChartInstance = null;

    // Initialize
    init();

    function init() {
        loadAvailableMethods();
        setupEventListeners();
        setupAnalysisTypeToggle();

        // Check for existing images in localStorage
        checkStoredImages();
    }

    function setupEventListeners() {
        // File input changes
        elements.image1.addEventListener('change', handleImageUpload);
        elements.image2.addEventListener('change', handleImageUpload);

        // Analysis type toggle
        elements.singleAnalysis.addEventListener('change', setupAnalysisTypeToggle);
        elements.compareAnalysis.addEventListener('change', setupAnalysisTypeToggle);

        // Action buttons
        elements.analyzeBtn.addEventListener('click', handleAnalyze);
        elements.clearBtn.addEventListener('click', handleClear);

        // Prevent page reload on beforeunload
        window.addEventListener('beforeunload', handleBeforeUnload);
        window.addEventListener('unload', handleUnload);
    }

    async function loadAvailableMethods() {
        try {
            const response = await fetch('/available-methods');
            availableMethods = await response.json();

            populateMethodSelect();
            populateMethodCheckboxes();
        } catch (error) {
            console.error('Error loading methods:', error);
            showToast('Error loading available methods', 'error');
        }
    }

    function populateMethodSelect() {
        elements.methodSelect.innerHTML = '<option value="">Select a method...</option>';

        // Add custom methods
        const customGroup = document.createElement('optgroup');
        customGroup.label = 'Custom Implementations';
        availableMethods.custom_methods.forEach(method => {
            const option = document.createElement('option');
            option.value = method;
            option.textContent = method;
            customGroup.appendChild(option);
        });
        elements.methodSelect.appendChild(customGroup);

        // Add library methods
        const libraryGroup = document.createElement('optgroup');
        libraryGroup.label = 'Library Methods';
        availableMethods.library_methods.forEach(method => {
            const option = document.createElement('option');
            option.value = method;
            option.textContent = method;
            libraryGroup.appendChild(option);
        });
        elements.methodSelect.appendChild(libraryGroup);
    }

    function populateMethodCheckboxes() {
        let html = '';

        // Custom methods
        html += '<div class="mb-3"><h6 class="text-primary">Custom Implementations</h6>';
        availableMethods.custom_methods.forEach(method => {
            html += `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${method}" id="method_${method.replace(/\s+/g, '_')}">
                    <label class="form-check-label custom-method" for="method_${method.replace(/\s+/g, '_')}">
                        ${method}
                    </label>
                </div>
            `;
        });
        html += '</div>';

        // Library methods
        html += '<div class="mb-3"><h6 class="text-success">Library Methods</h6>';
        availableMethods.library_methods.forEach(method => {
            html += `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${method}" id="method_${method.replace(/\s+/g, '_')}">
                    <label class="form-check-label library-method" for="method_${method.replace(/\s+/g, '_')}">
                        ${method}
                    </label>
                </div>
            `;
        });
        html += '</div>';

        // Select all buttons
        html += `
            <div class="d-grid gap-1">
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="selectAllMethods('custom')">
                    Select All Custom
                </button>
                <button type="button" class="btn btn-sm btn-outline-success" onclick="selectAllMethods('library')">
                    Select All Library
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="selectAllMethods('none')">
                    Clear Selection
                </button>
            </div>
        `;

        elements.methodCheckboxes.innerHTML = html;
    }

    // Make selectAllMethods globally available
    window.selectAllMethods = function (type) {
        const checkboxes = elements.methodCheckboxes.querySelectorAll('input[type="checkbox"]');

        checkboxes.forEach(checkbox => {
            if (type === 'none') {
                checkbox.checked = false;
            } else if (type === 'custom') {
                checkbox.checked = availableMethods.custom_methods.includes(checkbox.value);
            } else if (type === 'library') {
                checkbox.checked = availableMethods.library_methods.includes(checkbox.value);
            }
        });
    };

    function setupAnalysisTypeToggle() {
        const isSingleAnalysis = elements.singleAnalysis.checked;

        elements.singleMethodPanel.style.display = isSingleAnalysis ? 'block' : 'none';
        elements.compareMethodPanel.style.display = isSingleAnalysis ? 'none' : 'block';

        // Reset results and metrics
        hideResults();
        hideMetrics();
    }

    function handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const imageId = event.target.id;
            const containerId = imageId + 'Container';

            // Store in localStorage
            localStorage.setItem(imageId, e.target.result);

            // Display preview
            displayImagePreview(containerId, e.target.result);

            // Show preview container if both images are loaded
            if (localStorage.getItem('image1') && localStorage.getItem('image2')) {
                elements.imagePreviewContainer.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }

    function displayImagePreview(containerId, imageSrc) {
        const container = document.getElementById(containerId);
        container.innerHTML = `<img src="${imageSrc}" class="image-preview" alt="Image preview">`;
    }

    function checkStoredImages() {
        const image1Data = localStorage.getItem('image1');
        const image2Data = localStorage.getItem('image2');

        if (image1Data || image2Data) {
            const shouldClear = confirm('Found previously uploaded images. Clear them?');
            if (shouldClear) {
                handleClear();
            } else {
                if (image1Data) displayImagePreview('image1Container', image1Data);
                if (image2Data) displayImagePreview('image2Container', image2Data);
                if (image1Data && image2Data) {
                    elements.imagePreviewContainer.style.display = 'block';
                }
            }
        }
    }

    async function handleAnalyze() {
        const image1Data = localStorage.getItem('image1');
        const image2Data = localStorage.getItem('image2');

        if (!image1Data || !image2Data) {
            showToast('Please upload both images before analyzing', 'warning');
            return;
        }

        const isSingleAnalysis = elements.singleAnalysis.checked;

        if (isSingleAnalysis) {
            const selectedMethod = elements.methodSelect.value;
            if (!selectedMethod) {
                showToast('Please select a method for analysis', 'warning');
                return;
            }
            await performSingleAnalysis(selectedMethod);
        } else {
            const selectedMethods = getSelectedMethods();
            if (selectedMethods.length === 0) {
                showToast('Please select at least one method for comparison', 'warning');
                return;
            }
            await performComparisonAnalysis(selectedMethods);
        }
    }

    function getSelectedMethods() {
        const checkboxes = elements.methodCheckboxes.querySelectorAll('input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    async function performSingleAnalysis(methodName) {
        try {
            showLoading(true);

            const formData = new FormData();
            formData.append('image1', dataURItoBlob(localStorage.getItem('image1')), 'image1.png');
            formData.append('image2', dataURItoBlob(localStorage.getItem('image2')), 'image2.png');
            formData.append('method_name', methodName);

            const response = await fetch('/single-method', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Analysis failed');
            }

            const imageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(imageBlob);

            // Display result
            elements.resultImage.src = imageUrl;
            showSingleResult();

            // Get metrics (separate call needed)
            await getSingleMethodMetrics(methodName);

            showToast('Analysis completed successfully', 'success');

        } catch (error) {
            console.error('Single analysis error:', error);
            showToast(`Analysis failed: ${error.message}`, 'error');
        } finally {
            showLoading(false);
        }
    }

    async function getSingleMethodMetrics(methodName) {
        try {
            const formData = new FormData();
            formData.append('image1', dataURItoBlob(localStorage.getItem('image1')), 'image1.png');
            formData.append('image2', dataURItoBlob(localStorage.getItem('image2')), 'image2.png');

            const response = await fetch('/compare-methods', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const allResults = await response.json();
                const methodResult = allResults[methodName];

                if (methodResult && methodResult.success) {
                    displaySingleMethodMetrics(methodResult);
                }
            }
        } catch (error) {
            console.error('Error getting metrics:', error);
        }
    }

    function displaySingleMethodMetrics(result) {
        elements.executionTime.textContent = result.execution_time + 's';
        elements.meanMagnitude.textContent = result.statistics.mean_magnitude?.toFixed(2) || '-';
        elements.maxMagnitude.textContent = result.statistics.max_magnitude?.toFixed(2) || '-';

        elements.singleMetrics.style.display = 'block';
        elements.comparisonMetrics.style.display = 'none';
        elements.metricsContainer.style.display = 'block';
        elements.emptyMetrics.style.display = 'none';
    }

    async function performComparisonAnalysis(selectedMethods) {
        try {
            showLoading(true);

            const formData = new FormData();
            formData.append('image1', dataURItoBlob(localStorage.getItem('image1')), 'image1.png');
            formData.append('image2', dataURItoBlob(localStorage.getItem('image2')), 'image2.png');

            // Get comparison data
            const metricsResponse = await fetch('/compare-methods', {
                method: 'POST',
                body: formData
            });

            if (!metricsResponse.ok) {
                throw new Error('Failed to get comparison metrics');
            }

            const allResults = await metricsResponse.json();

            // Filter results to only include selected methods
            const filteredResults = {};
            selectedMethods.forEach(method => {
                if (allResults[method]) {
                    filteredResults[method] = allResults[method];
                }
            });

            // Get visualization
            const vizFormData = new FormData();
            vizFormData.append('image1', dataURItoBlob(localStorage.getItem('image1')), 'image1.png');
            vizFormData.append('image2', dataURItoBlob(localStorage.getItem('image2')), 'image2.png');
            vizFormData.append('selected_methods', JSON.stringify(selectedMethods));

            const vizResponse = await fetch('/visualize-comparison', {
                method: 'POST',
                body: vizFormData
            });

            if (!vizResponse.ok) {
                throw new Error('Failed to generate comparison visualization');
            }

            const imageBlob = await vizResponse.blob();
            const imageUrl = URL.createObjectURL(imageBlob);

            // Display results
            elements.comparisonImage.src = imageUrl;
            showComparisonResult();

            // Display metrics
            displayComparisonMetrics(filteredResults);

            showToast('Comparison completed successfully', 'success');

        } catch (error) {
            console.error('Comparison analysis error:', error);
            showToast(`Comparison failed: ${error.message}`, 'error');
        } finally {
            showLoading(false);
        }
    }

    function displayComparisonMetrics(results) {
        // Create execution time chart
        createTimeChart(results);

        // Create methods list with detailed metrics
        createMethodsList(results);

        elements.singleMetrics.style.display = 'none';
        elements.comparisonMetrics.style.display = 'block';
        elements.metricsContainer.style.display = 'block';
        elements.emptyMetrics.style.display = 'none';
    }

    function createTimeChart(results) {
        const ctx = elements.timeChart.getContext('2d');

        // Destroy existing chart
        if (currentChartInstance) {
            currentChartInstance.destroy();
        }

        const methods = Object.keys(results);
        const times = methods.map(method => results[method].execution_time || 0);
        const colors = methods.map(method =>
            results[method].category === 'Custom' ? '#0d6efd' : '#198754'
        );

        currentChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: methods.map(m => m.replace(/ \(.*\)/, '')), // Remove parentheses for display
                datasets: [{
                    label: 'Execution Time (s)',
                    data: times,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Execution Time Comparison'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Time (seconds)'
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45
                        }
                    }
                }
            }
        });
    }

    function createMethodsList(results) {
        let html = '';

        Object.entries(results).forEach(([methodName, result]) => {
            const categoryClass = result.category === 'Custom' ? 'custom-method' : 'library-method';
            const statusBadge = result.success ?
                '<span class="badge bg-success">Success</span>' :
                '<span class="badge bg-danger">Failed</span>';

            html += `
                <div class="card mb-2">
                    <div class="card-body p-2">
                        <div class="d-flex justify-content-between align-items-start mb-1">
                            <h6 class="card-title mb-0 ${categoryClass}">${methodName}</h6>
                            ${statusBadge}
                        </div>
                        ${result.success ? `
                            <small class="text-muted">
                                Time: ${result.execution_time}s | 
                                Mean Mag: ${result.statistics.mean_magnitude?.toFixed(2) || 'N/A'}
                            </small>
                            ${result.comparison_metrics ? `
                                <div class="mt-1">
                                    <small class="text-info">
                                        MSE: ${result.comparison_metrics.mse} | 
                                        MAE: ${result.comparison_metrics.mae}
                                    </small>
                                </div>
                            ` : ''}
                        ` : `
                            <small class="text-danger">${result.error || 'Unknown error'}</small>
                        `}
                    </div>
                </div>
            `;
        });

        elements.methodsList.innerHTML = html;
    }

    function showSingleResult() {
        elements.resultContainer.style.display = 'block';
        elements.singleResult.style.display = 'block';
        elements.comparisonResult.style.display = 'none';
        elements.emptyResult.style.display = 'none';
    }

    function showComparisonResult() {
        elements.resultContainer.style.display = 'block';
        elements.singleResult.style.display = 'none';
        elements.comparisonResult.style.display = 'block';
        elements.emptyResult.style.display = 'none';
    }

    function hideResults() {
        elements.resultContainer.style.display = 'none';
        elements.emptyResult.style.display = 'block';
    }

    function hideMetrics() {
        elements.metricsContainer.style.display = 'none';
        elements.emptyMetrics.style.display = 'block';
    }

    function showLoading(show) {
        elements.loadingOverlay.style.display = show ? 'flex' : 'none';
        elements.analyzeSpinner.style.display = show ? 'inline-block' : 'none';
        elements.analyzeBtn.disabled = show;

        if (show) {
            elements.analyzeBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2"></span>
                <i class="bi bi-play-circle"></i> Analyzing...
            `;
        } else {
            elements.analyzeBtn.innerHTML = `
                <i class="bi bi-play-circle"></i> Analyze Motion
            `;
        }
    }

    function handleClear() {
        // Clear localStorage
        localStorage.removeItem('image1');
        localStorage.removeItem('image2');

        // Clear file inputs
        elements.image1.value = '';
        elements.image2.value = '';

        // Clear previews
        elements.image1Container.innerHTML = '';
        elements.image2Container.innerHTML = '';
        elements.imagePreviewContainer.style.display = 'none';

        // Hide results and metrics
        hideResults();
        hideMetrics();

        // Reset form
        elements.singleAnalysis.checked = true;
        setupAnalysisTypeToggle();

        showToast('All data cleared', 'info');
    }

    function handleBeforeUnload(e) {
        if (localStorage.getItem('image1') || localStorage.getItem('image2')) {
            e.returnValue = 'You have images saved—reloading will clear them.';
            return e.returnValue;
        }
    }

    function handleUnload() {
        // Clear on unload
        localStorage.removeItem('image1');
        localStorage.removeItem('image2');
    }

    // Utility functions
    function dataURItoBlob(dataURI) {
        const byteString = atob(dataURI.split(',')[1]);
        const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        return new Blob([ab], { type: mimeString });
    }

    function showToast(message, type = 'info') {
        // Create toast element
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        // Create or get toast container
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1100';
            document.body.appendChild(toastContainer);
        }

        // Add toast
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);

        // Initialize and show toast
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

})(); 