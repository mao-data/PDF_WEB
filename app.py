from flask import Flask, request, send_file, send_from_directory, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from utils import process_pdf
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='build', static_url_path='/')
# Enable CORS for all routes
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Set file permissions
os.chmod(UPLOAD_FOLDER, 0o777)
os.chmod(OUTPUT_FOLDER, 0o777)

# Serve React App
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

# Serve static files
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/process-pdf', methods=['POST'])
def process_pdf_route():
    try:
        logger.info("Received PDF processing request")
        
        if 'pdf' not in request.files:
            logger.error("No file in request")
            return 'No file uploaded', 400
        
        file = request.files['pdf']
        if file.filename == '':
            logger.error("Empty filename")
            return 'No file selected', 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f'processed_{filename}')
        
        logger.info(f"Saving file to {input_path}")
        file.save(input_path)
        
        try:
            # Process the PDF
            logger.info("Starting PDF processing")
            process_pdf(input_path, output_path)
            
            # Check if output file exists
            if not os.path.exists(output_path):
                raise Exception("Output file was not created")
                
            logger.info("PDF processed successfully")
            
            # Return the processed file
            return send_file(
                output_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='processed.pdf'
            )
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            logger.error(traceback.format_exc())
            return f"Error processing PDF: {str(e)}", 500
        finally:
            # Clean up files
            logger.info("Cleaning up files")
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Server error: {str(e)}", 500

# Add a test endpoint
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Flask server is running!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port) 