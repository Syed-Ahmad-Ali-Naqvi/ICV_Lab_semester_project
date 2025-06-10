// IIFE to scope and run on load
(function () {
    const img1Input = document.getElementById('image1');
    const img2Input = document.getElementById('image2');
    const clearBtn = document.getElementById('clearImages');
    const detectMotion = document.getElementById('detectMotion');

    clearBtn.addEventListener('click', clearStorage);
    detectMotion.addEventListener('click', detectMotionHandler);

    async function detectMotionHandler() {
        const dataUrl1 = localStorage.getItem('image1');
        const dataUrl2 = localStorage.getItem('image2');

        if (!dataUrl1 || !dataUrl2) {
            alert('Please upload both images before detecting motion.');
            return;
        }

        // Convert data-URLs back to Blobs
        const blob1 = await (await fetch(dataUrl1)).blob();
        const blob2 = await (await fetch(dataUrl2)).blob();

        // Wrap them in File objects (you can choose any filename)
        const file1 = new File([blob1], 'image1.png', { type: blob1.type });
        const file2 = new File([blob2], 'image2.png', { type: blob2.type });

        // Build multipart/form-data
        const formData = new FormData();
        formData.append('image1', file1);
        formData.append('image2', file2);

        try {
            const resp = await fetch('/submit', {
                method: 'POST',
                body: formData
                // **DO NOT** set Content-Type: the browser will do it for you
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const json = await resp.json();
            console.log('Server response:', json);
            // …handle/display your motion-detection result…
        } catch (err) {
            console.error('Upload failed:', err);
            alert('Upload failed: ' + err.message);
        }
    }

    // 1) On page load: if storage has images, ask to clear or keep
    const has1 = localStorage.getItem('image1'),
        has2 = localStorage.getItem('image2');
    if (has1 || has2) {
        if (confirm('Found previously uploaded images. Clear them?')) {
            clearStorage();
        } else {
            displayImages();
        }
    }

    // 2) Whenever either file input changes, if *both* are set → save & display
    img1Input.addEventListener('change', trySaveAndDisplay1);
    img2Input.addEventListener('change', trySaveAndDisplay2);

    // 3) Clear button
    clearBtn.addEventListener('click', clearStorage);

    // helper: once both inputs have files, trigger save/display
    function trySaveAndDisplay1() {
        const f1 = img1Input.files[0];
        if (f1) saveAndDisplayImages(f1, "f1");
    }
    function trySaveAndDisplay2() {
        const f2 = img2Input.files[0];
        if (f2) saveAndDisplayImages(f2, "f2");
    }

    // read two File objects → localStorage → UI
    function saveAndDisplayImages(f, fileType) {
        const r = new FileReader();

        if (fileType === "f1") {
            r.onload = e => {
                localStorage.setItem('image1', e.target.result);
                displaySingleImage('image1', 'image1Container');
            };
        } else if (fileType === "f2") {
            r.onload = e => {
                localStorage.setItem('image2', e.target.result);
                displaySingleImage('image2', 'image2Container');
            };
        }

        r.readAsDataURL(f);
    }

    // pull both keys → UI
    function displayImages() {
        displaySingleImage('image1', 'image1Container');
        displaySingleImage('image2', 'image2Container');
    }

    // draw one image in its container
    function displaySingleImage(key, containerId) {
        const data = localStorage.getItem(key);
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        if (!data) return;
        const img = new Image();
        img.src = data;
        img.style.maxWidth = '200px';
        img.style.maxHeight = '200px';
        container.appendChild(img);
    }

    // wipe storage + UI
    function clearStorage() {
        localStorage.removeItem('image1');
        localStorage.removeItem('image2');
        document.getElementById('image1Container').innerHTML = '';
        document.getElementById('image2Container').innerHTML = '';
    }


})();
