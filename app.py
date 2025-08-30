from flask import Flask, request, render_template
import os 
import sys
import json 
import faiss 
from PIL import Image

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
index = faiss.read_index(INDEX_FILE)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # Just the form

@app.route("/results", methods=["POST"])
def results():
    file = request.files.get("file")
    num_results = request.form.get("num")
    if not file:
        return render_template("index.html", error_message="Please input a valid image")
    try:
        img = Image.open(file.stream)
    except Exception as e:
        return render_template("index.html", error_message=f"Image cannot be converted: {e}")
    emb = convert_img_to_embedding(img)
    final_list = find_k_similar(emb, index, metadata_hash, num_results)
    return render_template("results.html", results=final_list)
    
