// (function () {
//     const img1Input = document.getElementById('image1');
//     const img2Input = document.getElementById('image2');
//     const clearBtn = document.getElementById('clearImages');
//     const detectMotion = document.getElementById('detectMotion');

//     clearBtn.addEventListener('click', clearStorage);
//     detectMotion.addEventListener('click', detectMotionHandler);

//     async function detectMotionHandler() {
//         const dataUrl1 = localStorage.getItem('image1');
//         const dataUrl2 = localStorage.getItem('image2');

//         if (!dataUrl1 || !dataUrl2) {    
//             alert('Please upload both images before detecting motion.');
//             return;
//         }

//         // Convert data-URLs back to Blobs
//         const blob1 = await (await fetch(dataUrl1)).blob();
//         const blob2 = await (await fetch(dataUrl2)).blob();

//         // Wrap them in File objects (you can choose any filename)
//         const file1 = new File([blob1], 'image1.png', { type: blob1.type });
//         const file2 = new File([blob2], 'image2.png', { type: blob2.type });

//         // Build multipart/form-data
//         formData.append('image1', file1);
//         formData.append('image2', file2);

//         try {
//             const resp = await fetch('/submit', {
//                 method: 'POST',
//                 body: formData
//                 // **DO NOT** set Content-Type: the browser will do it for you
//             });
//             if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
//             const json = await resp.json();
//             console.log('Server response:', json);
//             // …handle/display your motion-detection result…
//         } catch (err) {
//             console.error('Upload failed:', err);
//             alert('Upload failed: ' + err.message);
//         }

//     // 1) On page load: if storage has images, ask to clear or keep
//     const has1 = localStorage.getItem('image1'),
//         has2 = localStorage.getItem('image2');
//     if (has1 || has2) {
//         if (confirm('Found previously uploaded images. Clear them?')) {
//             clearStorage();
//         } else {
//             displayImages();
//         }
//     }

//     // 2) Whenever either file input changes, if *both* are set → save & display
//     img1Input.addEventListener('change', trySaveAndDisplay1);
//     img2Input.addEventListener('change', trySaveAndDisplay2);

//     // 3) Clear button
//     clearBtn.addEventListener('click', clearStorage);

//     // helper: once both inputs have files, trigger save/display
//     function trySaveAndDisplay1() {
//         const f1 = img1Input.files[0];
//         if (f1) saveAndDisplayImages(f1, "f1");
//     }
//     function trySaveAndDisplay2() {
//         const f2 = img2Input.files[0];
//         if (f2) saveAndDisplayImages(f2, "f2");
//     }

//     // read two File objects → localStorage → UI
//     function saveAndDisplayImages(f, fileType) {
//         const r = new FileReader();

//         if (fileType === "f1") {
//             r.onload = e => {
//                 localStorage.setItem('image1', e.target.result);
//                 displaySingleImage('image1', 'image1Container');
//             };
//         } else if (fileType === "f2") {
//             r.onload = e => {
//                 localStorage.setItem('image2', e.target.result);
//                 displaySingleImage('image2', 'image2Container');
//             };
//         }

//         r.readAsDataURL(f);
//     }

//     // pull both keys → UI
//     function displayImages() {
//         displaySingleImage('image1', 'image1Container');
//         displaySingleImage('image2', 'image2Container');
//     }

//     // draw one image in its container
//     function displaySingleImage(key, containerId) {
//         const data = localStorage.getItem(key);
//         const container = document.getElementById(containerId);
//         container.innerHTML = '';
//         if (!data) return;
//         const img = new Image();
//         img.src = data;
//         img.style.maxWidth = '200px';
//         img.style.maxHeight = '200px';
//         container.appendChild(img);
//     }

//     // wipe storage + UI
//     function clearStorage() {
//         localStorage.removeItem('image1');
//         localStorage.removeItem('image2');
//         document.getElementById('image1Container').innerHTML = '';
//         document.getElementById('image2Container').innerHTML = '';
//     }


// })();

// (function () {
//     const inputs = [
//         { id: 'image1', key: 'image1', container: 'image1Container' },
//         { id: 'image2', key: 'image2', container: 'image2Container' }
//     ];

//     const clearBtn = document.getElementById('clearImages');
//     const methodSSD = document.getElementById('methodSSD');
//     const methodHS = document.getElementById('methodHS');
//     const methodLK = document.getElementById('methodLK');
//     const resultContainer = document.getElementById('resultContainer');
//     const resultDiv = document.getElementById('result');

//     // 2) On page load: if any images are in localStorage, ask user to clear or keep
//     if (inputs.some(({ key }) => localStorage.getItem(key))) {
//         if (confirm('Found previously uploaded images. Clear them?')) {
//             clearAll();
//         } else {
//             displayAll();
//         }
//     }

//     // 3) Wire up each <input type="file"> to save & display immediately
//     inputs.forEach(({ id, key, container }) => {
//         document.getElementById(id).addEventListener('change', (e) => {
//             const file = e.target.files[0];
//             if (!file) return;
//             const reader = new FileReader();
//             reader.onload = ev => {
//                 localStorage.setItem(key, ev.target.result);
//                 displaySingle(key, container);
//             };
//             reader.readAsDataURL(file);
//         });
//     });

//     // 4) Clear button wipes storage, UI, and hides any result
//     clearBtn.addEventListener('click', () => {
//         clearAll();
//         hideResult();
//     });

//     // 5) “Detect Motion” button posts to /submit and shows returned image
//     methodSSD.addEventListener('click', detectMotionHandlerSSD);
//     methodHS.addEventListener('click', detectMotionHandlerHS);
//     methodLK.addEventListener('click', detectMotionHandlerLK);

//     // 6) Warn before reload/close if images exist; on unload actually clear
//     window.addEventListener('beforeunload', e => {
//         if (inputs.some(({ key }) => localStorage.getItem(key))) {
//             e.returnValue = 'You have images saved—reloading will clear them.';
//             return e.returnValue;
//         }
//     });
//     window.addEventListener('unload', clearAll);


//     /* ─── Handlers & Helpers ───────────────────────────────────── */

//     // Fetch motion‐detected PNG from server and display it
//     async function detectMotionHandlerSSD() {
//         // 1) Grab stored data‐URLs
//         const dataUrl1 = localStorage.getItem('image1');
//         const dataUrl2 = localStorage.getItem('image2');

//         if (!dataUrl1 || !dataUrl2) {
//             return alert('Please upload both images before detecting motion.');
//         }

//         // 2) Convert data‐URLs back into File objects
//         const blob1 = await (await fetch(dataUrl1)).blob();
//         const blob2 = await (await fetch(dataUrl2)).blob();
//         const file1 = new File([blob1], 'image1.png', { type: blob1.type });
//         const file2 = new File([blob2], 'image2.png', { type: blob2.type });

//         // 3) Build FormData and POST
//         const formData = new FormData();
//         formData.append('image1', file1);
//         formData.append('image2', file2);

//         try {
//             const resp = await fetch('/submitssd', {
//                 method: 'POST',
//                 body: formData
//             });
//             if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

//             // 4) Read response as Blob (PNG) and show it
//             const resultBlob = await resp.blob();
//             const imgUrl = URL.createObjectURL(resultBlob);

//             resultDiv.innerHTML = '';
//             const img = new Image();
//             img.src = imgUrl;
//             img.style.maxWidth = '100%';
//             resultDiv.appendChild(img);

//             resultContainer.style.display = 'block';
//         } catch (err) {
//             console.error('Motion detection failed:', err);
//             alert('Motion detection failed: ' + err.message);
//         }
//     }
//     async function detectMotionHandlerLK() {
//         // 1) Grab stored data‐URLs
//         const dataUrl1 = localStorage.getItem('image1');
//         const dataUrl2 = localStorage.getItem('image2');

//         if (!dataUrl1 || !dataUrl2) {
//             return alert('Please upload both images before detecting motion.');
//         }

//         // 2) Convert data‐URLs back into File objects
//         const blob1 = await (await fetch(dataUrl1)).blob();
//         const blob2 = await (await fetch(dataUrl2)).blob();
//         const file1 = new File([blob1], 'image1.png', { type: blob1.type });
//         const file2 = new File([blob2], 'image2.png', { type: blob2.type });

//         // 3) Build FormData and POST
//         const formData = new FormData();
//         formData.append('image1', file1);
//         formData.append('image2', file2);

//         try {
//             const resp = await fetch('/submitlk', {
//                 method: 'POST',
//                 body: formData
//             });
//             if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

//             // 4) Read response as Blob (PNG) and show it
//             const resultBlob = await resp.blob();
//             const imgUrl = URL.createObjectURL(resultBlob);

//             resultDiv.innerHTML = '';
//             const img = new Image();
//             img.src = imgUrl;
//             img.style.maxWidth = '100%';
//             resultDiv.appendChild(img);

//             resultContainer.style.display = 'block';
//         } catch (err) {
//             console.error('Motion detection failed:', err);
//             alert('Motion detection failed: ' + err.message);
//         }
//     }
//     async function detectMotionHandlerHS() {
//         // 1) Grab stored data‐URLs
//         const dataUrl1 = localStorage.getItem('image1');
//         const dataUrl2 = localStorage.getItem('image2');

//         if (!dataUrl1 || !dataUrl2) {
//             return alert('Please upload both images before detecting motion.');
//         }

//         // 2) Convert data‐URLs back into File objects
//         const blob1 = await (await fetch(dataUrl1)).blob();
//         const blob2 = await (await fetch(dataUrl2)).blob();
//         const file1 = new File([blob1], 'image1.png', { type: blob1.type });
//         const file2 = new File([blob2], 'image2.png', { type: blob2.type });

//         // 3) Build FormData and POST
//         const formData = new FormData();
//         formData.append('image1', file1);
//         formData.append('image2', file2);

//         try {
//             const resp = await fetch('/submiths', {
//                 method: 'POST',
//                 body: formData
//             });
//             if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

//             // 4) Read response as Blob (PNG) and show it
//             const resultBlob = await resp.blob();
//             const imgUrl = URL.createObjectURL(resultBlob);

//             resultDiv.innerHTML = '';
//             const img = new Image();
//             img.src = imgUrl;
//             img.style.maxWidth = '100%';
//             resultDiv.appendChild(img);

//             resultContainer.style.display = 'block';
//         } catch (err) {
//             console.error('Motion detection failed:', err);
//             alert('Motion detection failed: ' + err.message);
//         }
//     }

//     // Display all stored images in their containers
//     function displayAll() {
//         inputs.forEach(({ key, container }) => displaySingle(key, container));
//     }

//     // Display one image
//     function displaySingle(key, containerId) {
//         const data = localStorage.getItem(key);
//         const container = document.getElementById(containerId);
//         container.innerHTML = '';
//         if (!data) return;
//         const img = new Image();
//         img.src = data;
//         img.style.maxWidth = '200px';
//         img.style.borderRadius = '0.5rem';
//         container.appendChild(img);
//     }

//     // Clear localStorage and preview containers
//     function clearAll() {
//         inputs.forEach(({ key, container }) => {
//             localStorage.removeItem(key);
//             document.getElementById(container).innerHTML = '';
//         });
//     }

//     // Hide the result section
//     function hideResult() {
//         resultContainer.style.display = 'none';
//         resultDiv.innerHTML = '';
//     }

// })();

// static/script.js
(function () {
    // 1) Configure your two file‐inputs + preview containers
    const inputs = [
        { id: 'image1', key: 'image1', container: 'image1Container' },
        { id: 'image2', key: 'image2', container: 'image2Container' }
    ];

    // 2) Grab buttons and result area
    const clearBtn = document.getElementById('clearImages');
    const btnSSD = document.getElementById('methodSSD');
    const btnHS = document.getElementById('methodHS');
    const btnLK = document.getElementById('methodLK');
    const resultContainer = document.getElementById('resultContainer');
    const resultDiv = document.getElementById('result');

    // 3) On page load: offer to clear or keep stored previews
    if (inputs.some(({ key }) => localStorage.getItem(key))) {
        if (confirm('Found previously uploaded images. Clear them?')) {
            clearAll();
        } else {
            displayAll();
        }
    }

    // 4) Wire up each file‐input to save & preview immediately
    inputs.forEach(({ id, key, container }) => {
        document.getElementById(id).addEventListener('change', e => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = ev => {
                localStorage.setItem(key, ev.target.result);
                displaySingle(key, container);
            };
            reader.readAsDataURL(file);
        });
    });

    // 5) Clear button: wipe previews & hide result
    clearBtn.addEventListener('click', () => {
        clearAll();
        hideResult();
    });

    // 6) Method buttons all call the same handler with different method strings
    btnSSD.addEventListener('click', () => detectMotion('ssd'));
    btnHS.addEventListener('click', () => detectMotion('horn_schunck'));
    btnLK.addEventListener('click', () => detectMotion('pyr_lucas_kanade'));

    // 7) Prompt before unload, then actually clear on unload
    window.addEventListener('beforeunload', e => {
        if (inputs.some(({ key }) => localStorage.getItem(key))) {
            e.returnValue = 'You have images saved—reloading will clear them.';
            return e.returnValue;
        }
    });
    window.addEventListener('unload', clearAll);


    /* ─── Core function ───────────────────────────────────────────────── */

    async function detectMotion(method) {
        // a) get stored data‐URLs
        const dataUrl1 = localStorage.getItem('image1');
        const dataUrl2 = localStorage.getItem('image2');
        if (!dataUrl1 || !dataUrl2) {
            return alert('Please upload both images before detecting motion.');
        }

        // b) convert data‐URLs → Blobs → Files
        const blob1 = await (await fetch(dataUrl1)).blob();
        const blob2 = await (await fetch(dataUrl2)).blob();
        const file1 = new File([blob1], 'image1.png', { type: blob1.type });
        const file2 = new File([blob2], 'image2.png', { type: blob2.type });

        // c) build FormData including chosen method
        const formData = new FormData();
        formData.append('image1', file1);
        formData.append('image2', file2);
        formData.append('method_received', method);

        try {
            // d) POST to single /submit route
            const resp = await fetch('/submit', {
                method: 'POST',
                body: formData
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

            // e) read returned PNG and show it
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            resultDiv.innerHTML = '';
            const img = new Image();
            img.src = url;
            img.style.maxWidth = '100%';
            img.style.borderRadius = '0.5rem';
            resultDiv.appendChild(img);
            document.getElementById('resultContainer').classList.add('visible');
            resultContainer.style.display = 'block';
        } catch (err) {
            console.error('Motion detection failed:', err);
            alert('Motion detection failed: ' + err.message);
        }
    }


    /* ─── Utility Helpers ────────────────────────────────────────────── */

    function displayAll() {
        inputs.forEach(({ key, container }) => displaySingle(key, container));
    }

    function displaySingle(key, containerId) {
        const data = localStorage.getItem(key);
        const cont = document.getElementById(containerId);
        cont.innerHTML = '';
        if (!data) return;
        const img = new Image();
        img.src = data;
        img.style.maxWidth = '200px';
        img.style.borderRadius = '0.5rem';
        cont.appendChild(img);
    }

    function clearAll() {
        inputs.forEach(({ key, container }) => {
            localStorage.removeItem(key);
            document.getElementById(container).innerHTML = '';
        });
    }

    function hideResult() {
        resultContainer.style.display = 'none';
        resultDiv.innerHTML = '';
    }

})();