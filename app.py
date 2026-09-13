import os
import sys

# Set environment variables for headless OpenCV
os.environ['DISPLAY'] = ''
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from ultralytics import YOLO
import logging
from urllib.parse import urlparse
import requests
from io import BytesIO
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to hold the model (load once)
model = None
model_loading_error = None

def load_model():
    """Load the YOLO model once on demand (lazy loading)"""
    global model, model_loading_error
    if model is None and model_loading_error is None:
        logger.info("Loading YOLO model on demand...")
        try:
            # Load local YOLO model
            model_path = os.path.join(os.path.dirname(__file__), 'yolo26n.pt')
            logger.info(f"Loading YOLO model from {model_path}...")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"YOLO model file not found at {model_path}")
            
            model = YOLO(model_path)
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            model_loading_error = str(e)
            # Don't raise - let the request handle the error gracefully
    return model

def is_valid_url(url):
    """Validate if the URL is from allowed domains"""
    try:
        result = urlparse(url)
        # Allow Cloudinary, Unsplash, and other common image hosts
        allowed_domains = [
            'cloudinary.com',
            'res.cloudinary.com',
            'unsplash.com',
            'images.unsplash.com',
            'example.com'  # for testing
        ]
        return any(domain in result.netloc for domain in allowed_domains)
    except:
        return False

def download_image(url):
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        raise

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        "message": "Lettuce Disease Detection API - YOLO Model",
        "version": "2.0.0",
        "model_type": "YOLO",
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "predict_batch": "/predict/batch (POST)"
        },
        "status": "healthy",
        "model_loaded": model is not None,
        "model_error": model_loading_error
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "model_error": model_loading_error
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict plant disease from image URL using YOLO model
    Expected JSON body:
    {
        "image_url": "https://example.com/image.jpg"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'image_url' not in data:
            return jsonify({"error": "Missing image_url in request body"}), 400
        
        image_url = data['image_url']
        
        # Validate URL
        if not is_valid_url(image_url):
            return jsonify({"error": "Invalid or unauthorized image URL"}), 400
        
        logger.info(f"Processing image: {image_url}")
        
        # Load model if not already loaded
        yolo_model = load_model()
        if yolo_model is None:
            return jsonify({
                "error": f"Model failed to load: {model_loading_error}",
                "success": False
            }), 500
        
        # Download and process image
        image = download_image(image_url)
        
        # Run YOLO inference
        results = yolo_model(image)
        
        # Format YOLO results
        formatted_results = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = float(box.conf[0])
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                formatted_results.append({
                    "label": class_name,
                    "score": confidence,
                    "bbox": {
                        "x1": x1,
                        "y1": y1, 
                        "x2": x2,
                        "y2": y2
                    }
                })
        
        # Sort by confidence and get top result
        if formatted_results:
            formatted_results.sort(key=lambda x: x['score'], reverse=True)
            top_result = formatted_results[0]
            logger.info(f"Prediction completed: {top_result['label']} (confidence: {top_result['score']:.4f})")
        else:
            logger.info("No detections found")
        
        return jsonify({
            "success": True,
            "predictions": formatted_results
        })
        
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predict plant diseases from multiple image URLs using YOLO model
    Expected JSON body:
    {
        "image_urls": ["url1", "url2", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'image_urls' not in data:
            return jsonify({"error": "Missing image_urls in request body"}), 400
        
        image_urls = data['image_urls']
        
        if not isinstance(image_urls, list):
            return jsonify({"error": "image_urls must be an array"}), 400
        
        logger.info(f"Processing batch of {len(image_urls)} images")
        
        # Load model if not already loaded
        yolo_model = load_model()
        if yolo_model is None:
            return jsonify({
                "error": f"Model failed to load: {model_loading_error}",
                "success": False
            }), 500
        
        results = []
        for url in image_urls:
            try:
                if not is_valid_url(url):
                    results.append({
                        "image_url": url,
                        "error": "Invalid or unauthorized image URL",
                        "success": False
                    })
                    continue
                
                image = download_image(url)
                predictions = yolo_model(image)
                
                formatted_predictions = []
                for result in predictions:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        class_name = result.names[class_id]
                        confidence = float(box.conf[0])
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        formatted_predictions.append({
                            "label": class_name,
                            "score": confidence,
                            "bbox": {
                                "x1": x1,
                                "y1": y1, 
                                "x2": x2,
                                "y2": y2
                            }
                        })
                
                # Sort by confidence
                formatted_predictions.sort(key=lambda x: x['score'], reverse=True)
                
                results.append({
                    "image_url": url,
                    "predictions": formatted_predictions,
                    "success": True
                })
                
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                results.append({
                    "image_url": url,
                    "error": str(e),
                    "success": False
                })
        
        return jsonify({
            "success": True,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error during batch prediction: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

if __name__ == '__main__':
    # Don't load model at startup - use lazy loading to avoid memory issues
    logger.info("Application startup - YOLO model will be loaded on demand")
    
    # Run the app with production settings
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)