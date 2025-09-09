from flask import Flask, request, render_template, flash, redirect, url_for
import os 
import sys
import json 
import faiss 
from PIL import Image
import io 
import base64
import boto3
import tempfile # Allow for index to be a tempfile when saved from cloud
import psutil

# DIRECTORIES 
BASE_DIR = os.path.dirname(__file__) 
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")
INDEX_FILE = os.path.join(BASE_DIR, "faiss.index")

# Allow for imports 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from search import convert_img_to_embedding, find_k_similar

# Track memory usage from application 
def log_mem(stage=""):
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    print(f"[MEMORY] {stage}: {mem_mb:.2f} MB")

# Load index and json (should be existing already)
# CODE BELOW: Is for when metadata.json and faiss.index are in project directory
# with open(METADATA_FILE, "r") as f: 
#     metadata = json.load(f)
# faiss_index = faiss.read_index(INDEX_FILE)


# Load index and json from AWS S3 Cloud 
# Assume AWS keys are loaded via dotenv
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    config=boto3.session.Config(signature_version='s3v4'),
)
bucket = os.getenv("S3_BUCKET_NAME")

index_obj = s3.get_object(Bucket=bucket, Key="faiss.index")
index_bytes = index_obj['Body'].read()
with tempfile.NamedTemporaryFile(suffix=".faiss") as f:
    f.write(index_bytes)
    f.flush()  # make sure contents are written
    faiss_index = faiss.read_index(f.name)

metadata_obj = s3.get_object(Bucket=bucket, Key="metadata.json")
metadata = json.loads(metadata_obj['Body'].read().decode("utf-8"))
metadata_hash = {album["faiss_index"]: album for album in metadata}


app = Flask(__name__)

# Secret key for session signing (used by flash)
app.secret_key = os.environ.get('SECRET_KEY')


@app.route("/", methods=["GET"])
def index():
    log_mem("on open")
    return render_template("index.html")  # Just the form

@app.route("/results", methods=["POST"])
def results():
    file = request.files.get("image")
    log_mem("after opening image")
    num_results = request.form.get("num_results", type=int)
    if not file:
        flash("Please input a valid image", "error")
        return redirect(url_for('index'))
    try:
        img = Image.open(file.stream)

        # Convert image to base64 string
        buf = io.BytesIO()
        img.save(buf, format="PNG")  # always save as PNG (or use img.format)
        log_mem("after saving PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        img_data = f"data:image/png;base64,{img_b64}"
        log_mem("after base64 encoding")

    except Exception as e:
        flash(f"Image cannot be converted: {e}", "error")
        return redirect(url_for('index'))
    emb = convert_img_to_embedding(img)
    log_mem("after embedding")
    final_list = find_k_similar(emb, faiss_index, metadata_hash, num_results)
    log_mem("after FAISS query")

    # Add S3 URL for album images (REMOVE IF USING LOCAL FILES)
    for album in final_list:
        if "file_name" in album:
            album["album_url"] = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': bucket, 'Key': album["file_name"]},
                ExpiresIn=3600
            )

    return render_template("results.html", img=img_data, results=final_list, num_results=num_results)