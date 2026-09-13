# Lettuce Disease Detection Flask API - YOLO Model

Flask API for plant disease detection using a local YOLO model for deployment on Railway.

## Features

- Object detection for plant diseases using YOLO
- Batch processing support
- URL-based image input
- CORS enabled for cross-origin requests
- Health check endpoint
- Error handling and logging
- Local YOLO model (no Hugging Face API needed)
- Railway deployment ready

## Model

This API uses a local YOLO model (`yolo26n.pt`) for plant disease detection. The model is included in the repository for easy deployment to Railway without requiring external API payments.

## Endpoints

### Health Check
```
GET /health
```
Returns API health status and model loading state.

### Single Prediction
```
POST /predict
Content-Type: application/json

{
  "image_url": "https://example.com/image.jpg"
}
```

Returns YOLO detection results with bounding boxes and confidence scores.

### Batch Prediction
```
POST /predict/batch
Content-Type: application/json

{
  "image_urls": ["url1", "url2", "url3"]
}
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the YOLO model file `yolo26n.pt` is in the same directory as `app.py`

3. Run the API:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Testing

Run the test script:
```bash
python test_api.py
```

## Railway Deployment

### Prerequisites

- Railway account
- Git repository with this code
- `yolo26n.pt` model file committed to the repository

### Deployment Steps

1. **Push your code to GitHub** (including the `yolo26n.pt` file)

2. **Create a new Railway project**:
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure the service**:
   - Railway will auto-detect Python/Flask
   - Set the following environment variables if needed:
     - `PORT`: 5000 (default)
     - `FLASK_ENV`: production

4. **Deploy**:
   - Railway will automatically:
     - Install dependencies from `requirements.txt`
     - Start the service using the Procfile
     - Make your API available at a Railway URL

5. **Get your API URL**:
   - Once deployed, Railway will provide a URL like `https://your-app.railway.app`
   - Use this URL to integrate with your Supabase functions

### Railway Configuration Files

The repository includes:
- `requirements.txt` - Python dependencies
- `Procfile` - Railway process configuration (`web: gunicorn app:app`)
- `.gitignore` - Excludes unnecessary files (keeps `yolo26n.pt` for deployment)

### Environment Variables

No additional environment variables are required for basic operation. The API will automatically:
- Load the YOLO model from the local file
- Use Railway's assigned PORT
- Run in production mode

## Integration with Supabase

Once deployed to Railway, update your Supabase secrets:

```bash
supabase secrets set FLASK_API_URL=https://your-railway-app-url.railway.app
supabase secrets set AI_PROVIDER=flask-api
```

Then update your Supabase Edge Function to use the custom provider with your Railway API URL.

## API Response Format

### Single Prediction Response
```json
{
  "success": true,
  "predictions": [
    {
      "label": "disease_class",
      "score": 0.95,
      "bbox": {
        "x1": 100,
        "y1": 50,
        "x2": 300,
        "y2": 250
      }
    }
  ]
}
```

### Batch Prediction Response
```json
{
  "success": true,
  "results": [
    {
      "image_url": "https://example.com/image1.jpg",
      "predictions": [...],
      "success": true
    },
    {
      "image_url": "https://example.com/image2.jpg",
      "predictions": [...],
      "success": true
    }
  ]
}
```

## Security Notes

- The API validates image URLs to only allow specific domains
- Modify the `is_valid_url()` function in `app.py` to add your allowed domains
- Consider adding API key authentication for production use
- Railway provides SSL/TLS encryption automatically

## Troubleshooting

### Model Loading Issues
- Ensure `yolo26n.pt` is in the same directory as `app.py`
- Check Railway logs for model loading errors
- Verify the model file is not corrupted

### Memory Issues
- YOLO models can be memory-intensive
- Consider using Railway's paid tiers for better performance
- The API uses lazy loading to minimize memory usage

### Deployment Failures
- Check Railway build logs for dependency installation errors
- Ensure all requirements are properly specified in `requirements.txt`
- Verify the Procfile format is correct

## License

Apache-2.0