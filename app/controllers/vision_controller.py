"""
Computer Vision Controller for handling camera-based emergency detection
"""
import uuid
import time
import base64
import io
import json
from flask import current_app
import numpy as np
from PIL import Image, ImageDraw
from app.utils.aws_utils import s3_upload_file, dynamodb_put_item

# Placeholder for a real computer vision model
# In a production environment, this would be a proper ML model
# like YOLOv5, Faster R-CNN, or a custom TensorFlow/PyTorch model
class EmergencyDetectionModel:
    """Simple placeholder for a real computer vision model"""
    
    def __init__(self):
        """Initialize model"""
        self.detection_classes = [
            'vehicle', 'pedestrian', 'traffic_light', 'traffic_sign',
            'ambulance', 'police_car', 'fire_truck', 'maintenance_vehicle',
            'accident', 'fire', 'smoke', 'construction', 'road_closure'
        ]
    
    def detect(self, image_array):
        """
        Simulate detection on an image
        
        Args:
            image_array (numpy.ndarray): Image as numpy array
            
        Returns:
            list: List of detected objects with bounding boxes and confidence
        """
        # This is a placeholder that simulates detections
        # In a real system, this would use a proper CV model
        
        height, width = image_array.shape[:2]
        
        # Simulate some random detections
        num_detections = np.random.randint(0, 5)
        detections = []
        
        for _ in range(num_detections):
            # Random class
            class_id = np.random.randint(0, len(self.detection_classes))
            class_name = self.detection_classes[class_id]
            
            # Random bounding box
            x1 = np.random.randint(0, width - 100)
            y1 = np.random.randint(0, height - 100)
            w = np.random.randint(50, 100)
            h = np.random.randint(50, 100)
            
            # Random confidence
            confidence = np.random.uniform(0.6, 0.95)
            
            detections.append({
                'class': class_name,
                'confidence': float(confidence),
                'bbox': [int(x1), int(y1), int(x1 + w), int(y1 + h)]
            })
        
        return detections

# Initialize the model once
emergency_model = EmergencyDetectionModel()

def process_image(image_data, truck_id=None):
    """
    Process an image for emergency detection
    
    Args:
        image_data (str): Base64 encoded image data
        truck_id (str, optional): ID of the truck that sent the image
        
    Returns:
        dict: Detection results
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array for processing
        image_array = np.array(image)
        
        # Run detection
        detections = emergency_model.detect(image_array)
        
        # Determine if any emergency is detected
        emergency_classes = ['ambulance', 'police_car', 'fire_truck', 'accident', 'fire', 'smoke']
        is_emergency = any(
            d['class'] in emergency_classes and d['confidence'] > 0.75
            for d in detections
        )
        
        # Draw bounding boxes on image for visualization
        annotated_image = draw_detections(image, detections)
        
        # Save processed image to S3
        image_id = f"image-{uuid.uuid4()}"
        s3_bucket = current_app.config.get('S3_BUCKET_NAME')
        
        # Convert annotated image to bytes for upload
        buffer = io.BytesIO()
        annotated_image.save(buffer, format="JPEG")
        buffer.seek(0)
        
        # Upload to S3
        image_url = s3_upload_file(
            s3_bucket,
            buffer,
            f"vision/{image_id}.jpg",
            "image/jpeg"
        )
        
        # Create detection record
        detection_record = {
            'detection_id': f"detection-{uuid.uuid4()}",
            'timestamp': int(time.time()),
            'truck_id': truck_id,
            'image_url': image_url,
            'detections': detections,
            'is_emergency': is_emergency
        }
        
        # Save detection record to DynamoDB if this is a real emergency
        if is_emergency and truck_id:
            # Create an alert for this emergency
            from app.controllers.alert_controller import add_alert
            
            alert_data = {
                'truck_id': truck_id,
                'alert_type': 'vision_emergency',
                'severity': 'high',
                'message': f"Emergency detected in camera feed: {', '.join(d['class'] for d in detections if d['class'] in emergency_classes)}",
                'detection_id': detection_record['detection_id'],
                'image_url': image_url
            }
            
            add_alert(alert_data)
        
        return {
            'status': 'success',
            'detection_id': detection_record['detection_id'],
            'is_emergency': is_emergency,
            'detections': detections,
            'image_url': image_url
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def draw_detections(image, detections):
    """
    Draw bounding boxes and labels on an image
    
    Args:
        image (PIL.Image): Original image
        detections (list): List of detections with bounding boxes
        
    Returns:
        PIL.Image: Annotated image
    """
    # Create a copy of the image for drawing
    draw_image = image.copy()
    draw = ImageDraw.Draw(draw_image)
    
    # Color mapping for different classes
    colors = {
        'vehicle': (0, 255, 0),             # Green
        'pedestrian': (255, 255, 0),        # Yellow
        'traffic_light': (0, 255, 255),     # Cyan
        'traffic_sign': (255, 255, 0),      # Yellow
        'ambulance': (255, 0, 0),           # Red
        'police_car': (0, 0, 255),          # Blue
        'fire_truck': (255, 0, 0),          # Red
        'maintenance_vehicle': (255, 165, 0), # Orange
        'accident': (255, 0, 0),            # Red
        'fire': (255, 0, 0),                # Red
        'smoke': (128, 128, 128),           # Gray
        'construction': (255, 165, 0),      # Orange
        'road_closure': (255, 0, 255)       # Magenta
    }
    
    # Draw each detection
    for detection in detections:
        # Get bounding box coordinates
        x1, y1, x2, y2 = detection['bbox']
        
        # Get class and color
        class_name = detection['class']
        color = colors.get(class_name, (255, 255, 255))  # Default to white
        
        # Draw bounding box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        
        # Draw label with confidence
        label = f"{class_name} {detection['confidence']:.2f}"
        draw.text((x1, y1 - 10), label, fill=color)
    
    return draw_image

def get_recent_detections(limit=10):
    """
    Get recent vision detections
    
    Args:
        limit (int): Maximum number of detections to return
        
    Returns:
        list: List of recent detections
    """
    # In a real implementation, this would query DynamoDB for recent detections
    # For now, return a placeholder
    return [{
        'detection_id': f"detection-{i}",
        'timestamp': int(time.time()) - i * 60,  # One minute apart
        'truck_id': f"truck-{i % 5}",
        'is_emergency': i % 3 == 0,  # Every third detection is an emergency
        'image_url': f"https://example.com/vision/detection-{i}.jpg"
    } for i in range(limit)]
