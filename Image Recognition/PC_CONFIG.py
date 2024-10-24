import os

# Base directory for your project (automatically set to the script's directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration for Flask
HOST = '0.0.0.0'  # or '0.0.0.0' for external access
IMAGE_REC_PORT = 5000  # Port number for your Flask app

# File directory paths
FILE_DIRECTORY = os.path.join(BASE_DIR, 'data')  # Adjust according to your structure

# Directories for image processing
UPLOAD_FOLDER = os.path.join(FILE_DIRECTORY, 'image-rec', 'images')
ANNOTATED_IMAGES = os.path.join(FILE_DIRECTORY, 'image-rec', 'annotated_images')
ANNOTATED_ARCHIVE = os.path.join(FILE_DIRECTORY, 'image-rec', 'annotated_archive')
STITCHED_IMAGES = os.path.join(FILE_DIRECTORY, 'image-rec', 'stitched_images')
SAMPLE_IMAGES = os.path.join(FILE_DIRECTORY, 'image-rec', 'sample_images')

if __name__ == '__main__':
    # Ensure all necessary directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(ANNOTATED_IMAGES, exist_ok=True)
    os.makedirs(ANNOTATED_ARCHIVE, exist_ok=True)
    os.makedirs(STITCHED_IMAGES, exist_ok=True)
    os.makedirs(SAMPLE_IMAGES, exist_ok=True)
