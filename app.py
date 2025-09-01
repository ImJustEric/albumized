from flask import Flask, request, render_template, flash, redirect, url_for
import os 
import sys
import json 
import faiss 
from PIL import Image
import io 
import base64

# DIRECTORIES 
BASE_DIR = os.path.dirname(__file__) 
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")
INDEX_FILE = os.path.join(BASE_DIR, "faiss.index")

# Allow for imports 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from search import convert_img_to_embedding, find_k_similar

# Load index and json (should be existing already)
with open(METADATA_FILE, "r") as f: 
    metadata = json.load(f)
metadata_hash = {album["faiss_index"]:album for album in metadata}
faiss_index = faiss.read_index(INDEX_FILE)

app = Flask(__name__)

# Secret key for session signing (used by flash)
app.secret_key = os.environ.get('SECRET_KEY')


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # Just the form

@app.route("/results", methods=["POST"])
def results():
    file = request.files.get("image")
    num_results = request.form.get("num_results", type=int)
    if not file:
        flash("Please input a valid image", "error")
        return redirect(url_for('index'))
    try:
        img = Image.open(file.stream)

        # Convert image to base64 string
        buf = io.BytesIO()
        img.save(buf, format="PNG")  # always save as PNG (or use img.format)
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        img_data = f"data:image/png;base64,{img_b64}"

    except Exception as e:
        flash(f"Image cannot be converted: {e}", "error")
        return redirect(url_for('index'))
    emb = convert_img_to_embedding(img)
    final_list = find_k_similar(emb, faiss_index, metadata_hash, num_results)

    return render_template("results.html", img=img_data, results=final_list, num_results=num_results)