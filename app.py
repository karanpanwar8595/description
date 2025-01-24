from flask import Flask, request, jsonify, send_from_directory, render_template
from PIL import Image
import torch
import os
import uuid
from transformers import BlipProcessor, BlipForConditionalGeneration

app = Flask(__name__)

# Set up folder to store uploaded images
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize BLIP model and processor
try:
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
except Exception as e:
    print("Error loading the BLIP model: ", e)
    exit(1)  # Exit if model loading fails

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the uploaded file is of an allowed type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Serve the main HTML page."""
    return render_template('index.html')  # Serve index.html from the templates folder

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and description generation."""
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Generate a unique filename to avoid conflicts
    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Save the image to the uploads folder
        file.save(filepath)
    except Exception as e:
        return jsonify({"error": f"Failed to save the image: {str(e)}"}), 500

    try:
        # Process the image using BLIP model
        img = Image.open(filepath)
        inputs = processor(images=img, return_tensors="pt")
        out = model.generate(**inputs)
        description = processor.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        return jsonify({"error": f"Error processing the image: {str(e)}"}), 500

    # Return the description and the URL to the uploaded image
    image_url = f"/uploads/{filename}"
    return jsonify({"description": description, "image_url": image_url})

# Route to serve uploaded images from the uploads folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({"error": f"Failed to serve image: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
