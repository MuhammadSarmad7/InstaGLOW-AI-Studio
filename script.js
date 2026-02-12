document.getElementById('campaignForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Stop the page from reloading
    
    // 1. Lock the button so they can't click twice
    const btn = document.getElementById('generateBtn');
    const loader = document.getElementById('loader');
    btn.disabled = true;
    loader.style.display = 'block';
    
    // 2. Prepare the data
    const formData = new FormData(this);

    try {
        // 3. Send data to Python (app.py)
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });

        // 4. Get the answer
        const data = await response.json();

        if (data.status === 'success') {
            // --- THIS IS WHERE THE RESULT IS SHOWN ---
            
            // Show the Caption
            const finalCaption = document.getElementById('finalCaption');
            if (finalCaption) {
                // Formatting: Bold username + text
                finalCaption.innerHTML = `<strong>YourBrand</strong> ${data.caption.replace(/\n/g, '<br>')}`;
            }

            // Show the Image
            const finalImage = document.getElementById('finalImage');
            const placeholder = document.getElementById('resultPlaceholder');
            
            if (data.image) {
                finalImage.src = `data:image/jpeg;base64,${data.image}`;
                finalImage.style.display = 'block';
                if (placeholder) placeholder.style.display = 'none';
            }
        } else {
            alert("Server Error: " + data.message);
        }

    } catch (error) {
        alert("Connection Error: " + error);
    } finally {
        // Unlock the button
        btn.disabled = false;
        loader.style.display = 'none';
    }
});

// Helper for previewing upload
function previewFile() {
    const preview = document.getElementById('uploadPreview');
    const fileInput = document.getElementById('fileInput');
    const uploadText = document.getElementById('uploadText');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onloadend = function() {
            preview.src = reader.result;
            preview.style.display = 'block';
            if (uploadText) uploadText.style.display = 'none';
        }
        reader.readAsDataURL(file);
    }
}