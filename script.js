const API_URL = 'http://127.0.0.1:5000'; // Change to 'https://your-render-url.onrender.com' for Render

if (typeof document === 'undefined') {
    console.error('Error: This script must run in a browser environment, not Node.js.');
    module.exports = {};
} else {
    const fileForm = document.getElementById('file-upload-form');
    const textForm = document.getElementById('text-upload-form');
    const statusEl = document.getElementById('status');
    const similarityBar = document.getElementById('similarity-bar');
    const similarityProgress = document.getElementById('similarity-progress');
    const detailsEl = document.getElementById('details');

    if (!fileForm || !textForm || !statusEl || !similarityBar || !similarityProgress || !detailsEl) {
        console.error('Error: DOM elements missing. Check index.html IDs.');
        if (statusEl) {
            statusEl.classList.add('error');
            statusEl.textContent = 'Error: Page not loaded correctly. Please refresh.';
        }
        throw new Error('DOM elements missing');
    }

    function displayResults(data) {
        statusEl.textContent = data.status || 'Analysis completed.';
        if (data.error) {
            statusEl.classList.add('error');
            statusEl.textContent = `Error: ${data.error}`;
            similarityBar.style.display = 'none';
            detailsEl.innerHTML = '';
            return;
        }
        statusEl.classList.remove('error');
        const similarity = parseFloat(data.similarity) || 0;
        similarityBar.style.display = 'block';
        similarityProgress.style.width = `${Math.min(similarity, 100)}%`;
        let detailsHTML = '';
        if (data.file_name) detailsHTML += `<p>File Name: ${data.file_name}</p>`;
        if (data.text_preview) detailsHTML += `<p>Text Preview: ${data.text_preview}</p>`;
        if (data.similarity) detailsHTML += `<p>Similarity: ${data.similarity}</p>`;
        if (data.message) detailsHTML += `<p>${data.message}</p>`;
        if (data.duplicates && data.duplicates.length) {
            detailsHTML += `<h3>Duplicate Sections:</h3><ul>`;
            data.duplicates.forEach(duplicate => {
                detailsHTML += `<li>${duplicate.phrase} - Source: ${duplicate.source}</li>`;
            });
            detailsHTML += `</ul>`;
        }
        detailsEl.innerHTML = detailsHTML;
    }

    function showError(message) {
        statusEl.classList.add('error');
        statusEl.textContent = `Error: ${message}`;
        similarityBar.style.display = 'none';
        detailsEl.innerHTML = '';
    }

    fileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('file-input');
        if (!fileInput.files[0]) {
            showError('Please select a file.');
            return;
        }
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        statusEl.textContent = 'Analyzing file...';
        similarityBar.style.display = 'none';
        detailsEl.innerHTML = '';
        try {
            const response = await fetch(`${API_URL}/upload-file`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: Status ${response.status}, ${errorText || 'Unknown error'}`);
            }
            const data = await response.json();
            displayResults(data);
        } catch (error) {
            let errorMsg = error.message.includes('Failed to fetch')
                ? 'Cannot connect to server. Ensure the backend is running at http://127.0.0.1:5000.'
                : error.message;
            showError(`Failed to analyze file: ${errorMsg}`);
            console.error('File upload error:', error);
        }
    });

    textForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const textInput = document.getElementById('text-input').value;
        if (!textInput.trim()) {
            showError('Please enter text.');
            return;
        }
        const textData = { text: textInput };
        statusEl.textContent = 'Analyzing text...';
        similarityBar.style.display = 'none';
        detailsEl.innerHTML = '';
        try {
            const response = await fetch(`${API_URL}/upload-text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(textData)
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: Status ${response.status}, ${errorText || 'Unknown error'}`);
            }
            const data = await response.json();
            displayResults(data);
        } catch (error) {
            let errorMsg = error.message.includes('Failed to fetch')
                ? 'Cannot connect to server. Ensure the backend is running at http://127.0.0.1:5000.'
                : error.message;
            showError(`Failed to analyze text: ${errorMsg}`);
            console.error('Text upload error:', error);
        }
    });
}