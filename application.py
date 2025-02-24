import os
import google.generativeai as genai
from flask import Flask, render_template, request, Response, redirect, url_for
from flask_bootstrap import Bootstrap
from object_detection import *
from camera_settings import *
from PIL import Image  # Import Pillow to handle images

# Initialize Flask app
application = Flask(__name__)
Bootstrap(application)

# Configure upload folder
UPLOAD_FOLDER = "static/uploads"
application.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Google Gemini API
GOOGLE_API_KEY = "AIzaSyCtQADcmYCAkHwxLv3xzqcoZytFkyg8XSM"  # 🔹 Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Video Streaming
check_settings()
VIDEO = VideoStreaming()

# Function to analyze image using Gemini API
def analyze_image(image_path):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Updated to latest model

        # Open the image using PIL (Pillow)
        image = Image.open(image_path)

        # Send both an image and a text prompt
        response = model.generate_content(
            ["What objects are in this image? Describe them in detail.", image]
        )

        return response.text if response else "No information found."
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

# * Route for Live Object Detection (index.html)
@application.route("/")
def home():
    TITLE = "OBJECT DETECTION AI"
    return render_template("index.html", TITLE=TITLE)

@application.route("/video_feed")
def video_feed():
    """ Video streaming route. """
    return Response(
        VIDEO.show(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# * Route for Image Upload & Analysis (upload.html)
@application.route("/upload", methods=["GET", "POST"])
def upload():
    image_name = None
    description = None

    if request.method == "POST":
        if "image" not in request.files or request.files["image"].filename == "":
            return redirect(request.url)  # Redirect if no file is selected

        file = request.files["image"]
        if file:
            image_name = file.filename
            file_path = os.path.join(application.config["UPLOAD_FOLDER"], image_name)
            file.save(file_path)

            # Analyze the image using Gemini API
            description = analyze_image(file_path)

            return render_template("upload.html", image_name=image_name, description=description)

    return render_template("upload.html")

# * Camera Settings Routes
@application.route("/request_preview_switch")
def request_preview_switch():
    VIDEO.preview = not VIDEO.preview
    return "nothing"

@application.route("/request_flipH_switch")
def request_flipH_switch():
    VIDEO.flipH = not VIDEO.flipH
    return "nothing"

@application.route("/request_model_switch")
def request_model_switch():
    VIDEO.detect = not VIDEO.detect
    return "nothing"

@application.route("/request_exposure_down")
def request_exposure_down():
    VIDEO.exposure -= 1
    return "nothing"

@application.route("/request_exposure_up")
def request_exposure_up():
    VIDEO.exposure += 1
    return "nothing"

@application.route("/request_contrast_down")
def request_contrast_down():
    VIDEO.contrast -= 4
    return "nothing"

@application.route("/request_contrast_up")
def request_contrast_up():
    VIDEO.contrast += 4
    return "nothing"

@application.route("/reset_camera")
def reset_camera():
    STATUS = reset_settings()
    return "nothing"

if __name__ == "__main__":
    application.run(debug=True)
