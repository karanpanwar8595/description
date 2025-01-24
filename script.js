document.getElementById('uploadBtn').addEventListener('click', function() {
    var fileInput = document.getElementById('imageInput');
    var file = fileInput.files[0];
    if (!file) {
        alert("Please select an image first.");
        return;
    }

    var formData = new FormData();
    formData.append('image', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.description) {
            document.getElementById('description').textContent = data.description;
            var imageContainer = document.getElementById('imageContainer');
            imageContainer.innerHTML = `<img src="${data.image_url}" alt="Uploaded Image" style="max-width: 100%; height: auto;">`;
        } else {
            alert(data.error || 'Error processing the image');
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
});
