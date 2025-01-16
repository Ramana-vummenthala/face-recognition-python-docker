from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import io
import base64
from PIL import Image
import os

app = Flask(__name__)

def process_image_file(image_file):
    """Convert uploaded file to numpy array and get face encoding"""
    # Read image file into memory
    image_stream = io.BytesIO(image_file.read())
    image = Image.open(image_stream)
    
    # Convert PIL Image to numpy array
    image_array = np.array(image)
    
    # Find faces in the image
    face_locations = face_recognition.face_locations(image_array)
    
    if not face_locations:
        return None, "No face detected in the image"
    
    if len(face_locations) > 1:
        return None, "Multiple faces detected in the image. Please provide an image with a single face"
    
    # Get face encoding
    face_encoding = face_recognition.face_encodings(image_array, face_locations)[0]
    return face_encoding, None

@app.route('/compare-faces', methods=['POST'])
def compare_faces():
    # Check if both images are provided
    print("11111")
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({
            'error': 'Please provide both images',
            'required_params': {
                'image1': 'First image file',
                'image2': 'Second image file'
            }
        }), 400
    
    image1 = request.files['image1']
    image2 = request.files['image2']
    print("22222")
    
    # Process first image
    encoding1, error1 = process_image_file(image1)
    if error1:
        return jsonify({
            'error': f'Error processing first image: {error1}'
        }), 400
    
    # Process second image
    encoding2, error2 = process_image_file(image2)
    if error2:
        return jsonify({
            'error': f'Error processing second image: {error2}'
        }), 400
    
    # Compare face encodings
    face_distance = face_recognition.face_distance([encoding1], encoding2)[0]
    match = face_recognition.compare_faces([encoding1], encoding2)[0]
    
    # Calculate similarity percentage (0 distance = 100% match, 0.6 or higher distance = 0% match)
    similarity = max(0, min(100, (1 - face_distance) * 100))
    print(similarity, bool)
    # return "success"
    return jsonify({
        'match':  bool(match),
        'similarity_percentage': round(similarity, 2),
        'face_distance': float(face_distance),
        # 'analysis': {
        #     'high_confidence_match': face_distance < 0.4,
        #     'possible_match': 0.4 <= face_distance < 0.6,
        #     'likely_different_people': face_distance >= 0.6
        # }
    })

#########################

IMAGE_FOLDER = "images"


def process_image_base64(image_base64):
    """Convert base64 image to numpy array and get face encoding"""
    try:
        # Decode the base64 string into bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Convert bytes to PIL Image
        image_stream = io.BytesIO(image_bytes)
        image = Image.open(image_stream)
        
        # Convert PIL Image to numpy array
        image_array = np.array(image)
        
        # Find faces in the image
        face_locations = face_recognition.face_locations(image_array)
        
        if not face_locations:
            return None, "No face detected in the image"
        
        if len(face_locations) > 1:
            return None, "Multiple faces detected in the image. Please provide an image with a single face"
        
        # Get face encoding
        face_encoding = face_recognition.face_encodings(image_array, face_locations)[0]
        return face_encoding, None
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

def process_image_bytearray(image_bytearray):
    """Convert bytearray image to numpy array and get face encoding"""
    # Convert bytearray to PIL Image
    image_stream = io.BytesIO(image_bytearray)
    image = Image.open(image_stream)
    
    # Convert PIL Image to numpy array
    image_array = np.array(image)
    
    # Find faces in the image
    face_locations = face_recognition.face_locations(image_array)
    
    if not face_locations:
        return None, "No face detected in the image"
    
    if len(face_locations) > 1:
        return None, "Multiple faces detected in the image. Please provide an image with a single face"
    
    # Get face encoding
    face_encoding = face_recognition.face_encodings(image_array, face_locations)[0]
    return face_encoding, None

def image_to_bytearray(image_path):
    """Convert image from project folder to bytearray"""
    with open(image_path, 'rb') as image_file:
        return image_file.read()

@app.route('/compare-with-folder', methods=['POST'])
def compare_with_folder():
    # Check if the image bytearray is provided
    if 'image' not in request.json:
        return jsonify({
            'error': 'Please provide an image in bytearray format',
            'required_params': {
                'image': 'Image bytearray'
            }
        }), 400
    
    # Get the image bytearray from the request
    image_bytearray = request.json['image']
    
    # Process the sent image
    sent_encoding, error = process_image_base64(image_bytearray)
    if error:
        return jsonify({
            'error': f'Error processing sent image: {error}'
        }), 400
    
    # Initialize variables to store the best match
    best_match = None
    best_similarity = 0
    best_image_name = None
    
    # Iterate through images in the folder
    for image_name in os.listdir(IMAGE_FOLDER):
        image_path = os.path.join(IMAGE_FOLDER, image_name)
        
        # Convert image to bytearray
        try:
            folder_image_bytearray = image_to_bytearray(image_path)
        except Exception as e:
            return jsonify({
                'error': f'Error reading image {image_name}: {str(e)}'
            }), 400
        
        # Process the folder image
        folder_encoding, error = process_image_bytearray(folder_image_bytearray)
        if error:
            continue  # Skip images with errors (e.g., no face detected)
        
        # Compare face encodings
        face_distance = face_recognition.face_distance([sent_encoding], folder_encoding)[0]
        similarity = max(0, min(100, (1 - face_distance) * 100))
        
        # Update best match if current similarity is higher
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = folder_encoding
            best_image_name = image_name
    
    # If no match found
    if best_match is None:
        return jsonify({
            'error': 'No matching face found in the folder'
        }), 404
    
    # Return the best match details
    return jsonify({
        'best_match_image': best_image_name,
        'similarity_percentage': round(best_similarity, 2),
        'message': f'Best match found with {best_image_name}'
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
