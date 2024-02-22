from flask import Flask, request
import torch
import requests
import os
import boto3
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Load the model (this can be done once when the server starts)
model = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3").cpu()
convert_video = torch.hub.load("PeterL1n/RobustVideoMatting", "converter")

# Helper function to download video from URL
def download_video(video_url, file_path):
    response = requests.get(video_url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(f"Error downloading video: status code {response.status_code}")

# Helper function to upload a file to S3
def upload_to_s3(file_path, bucket_name, object_name=None):
    """Upload a file to an S3 bucket and return the file's URL."""
    if object_name is None:
        object_name = os.path.basename(file_path)
    else:
        # Generate a random UUID and encode it in the object name
        random_id = str(uuid.uuid4())
        filename, extension = os.path.splitext(object_name)
        object_name = f"{filename}_{random_id}{extension}"

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs={'ACL': 'public-read', 'ContentType': 'video/mp4'})

        location = s3_client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        s3_url = f"https://{bucket_name}.s3.{location}.amazonaws.com/{object_name}"
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise

# Define the API endpoint
@app.route('/videomatting', methods=['POST'])
def process_video():
    video_url = request.json.get('video_url')
    if not video_url:
        return {"error": "No video URL provided"}, 400

    temp_video_path = 'input.mp4'
    output_composition_path = str(uuid.uuid4())+".mp4"

    try:
        # Download video from the provided URL
        download_video(video_url, temp_video_path)

        # Process video
        convert_video(
            model,
            input_source=temp_video_path,
            output_type='video',
            output_composition=output_composition_path,
            output_video_mbps=4,
            seq_chunk=12,
            progress=True
        )

        # Upload output video to S3
        s3_bucket_name = os.getenv('S3_BUCKET')
        s3_object_name = 'output/' + os.path.basename(output_composition_path)
        s3_url = upload_to_s3(output_composition_path, s3_bucket_name, s3_object_name)
        
        # Return the S3 URL of the uploaded video
        return {"message": "Video processed and uploaded to S3", "s3_url": s3_url}

    except Exception as e:
        return {"error": str(e)}, 500
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(output_composition_path):
            os.remove(output_composition_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)