from flask import Flask, request, send_file
import torch
import requests
import os

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

# Define the API endpoint
@app.route('/videomatting', methods=['POST'])
def process_video():
    video_url = request.json.get('video_url')
    if not video_url:
        return {"error": "No video URL provided"}, 400

    temp_video_path = 'input.mp4'
    output_composition_path = 'com.mp4'

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

        # Send file as response
        return send_file(output_composition_path, as_attachment=True)

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