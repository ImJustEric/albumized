# Albumized

Do you wonder whether an image could be or has been used as an album cover? Albumized finds the most visually-similar album covers to an uploaded image using a ResNet-based embedding extractor and FAISS vector search.

This repo contains a small Flask app with an accessible upload UI, a results view and a FAISS index built from the local `albums/` images and `metadata.json`.

## Features
- Upload an image (drag & drop / file dialog) and request N nearest album covers.
- Results show cover thumbnail, album title, artist(s), and a link to the Spotify album.
- Covers are served from the contents of the local `albums/` folder (safe serve route).

## Current version 

The current version of Albumized currently can quickly and efficiently search for similar album covers from over **700+** artists and **5500+** individual album covers.

## Quick start
1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies (recommended in the venv)

```bash
pip install flask pillow numpy
# Torch + torchvision: platform-specific — see https://pytorch.org for an appropriate command
# FAISS: on many systems you can `pip install faiss-cpu`, but on macOS/Apple Silicon you may need conda:
#   conda install -c conda-forge faiss-cpu
```

3. Create a `.env` file at the project root with your secrets (do NOT commit this file):

```
SECRET_KEY=your_secret_here
SPOTIPY_CLIENT_ID=...
SPOTIPY_CLIENT_SECRET=...
SPOTIPY_REDIRECT_URI=...
```

Only `SECRET_KEY` is required for Flask `flash()` messages to work. Spotify credentials are optional unless you integrate the Spotify API.

4. Run the app (development)

```bash
export FLASK_APP=app.py
flask run
```

If you prefer to run without the Flask reloader (useful if you see native-library crashes), run the app directly without the reloader:

```bash
python -c "from app import app; app.run(debug=False)"
```

Open http://127.0.0.1:5000 in your browser.

## Usage
- On the index page choose an image and set `Num of albums` (how many nearest neighbors you want).
- The results page shows your image and a list of result cards with the album cover, title, artist(s), a Spotify link and a rank badge (#1 is most similar).

## Important files
- `app.py` — Flask application, endpoints and a safe `/cover/<idx>` route to serve album image files.
- `search.py` — converts input images into embeddings and queries FAISS for nearest neighbors.
- `model.py` — the embedding extractor wrapper (ResNet-based). The app uses lazy model instantiation to avoid import-time native initializations. Also creates FAISS to be used
- `metadata.json` — metadata for each album (album name, artist, spotify_url, file_name, faiss_index). See section below for how to generate.
- `faiss.index` — pre-built FAISS index (binary) used by the app.
- `albums/` — local album cover image files referenced by `metadata.json`.
- `templates/`, `static/` — frontend (HTML, CSS, JS, images).

## Album generation, metadata.json
The repository includes a helper script `extract_album_covers.py` that is intended to build the `metadata.json` file the app uses as its catalog.

- Purpose: scan or accept manual entries for album cover images and produce a JSON manifest (`metadata.json`) containing fields such as `file_name`, `id`, `name`, `artist`, `spotify_url`, and `faiss_index`.
- Manual input: the script supports entering albums manually (so you can curate which images become part of the database) — this is useful if you have a small set of covers or want to annotate them with artist/Spotify links.
- Output: writes (or updates) `metadata.json` in the repo root which the Flask app and FAISS search use to map search results to album files and external URLs.

Notes:
- After updating `metadata.json` you will need a FAISS index that corresponds to the entries (the repo uses `faiss.index`). If you change the set of albums you may need to rebuild the FAISS index so `faiss_index` values match.
- You can also edit `metadata.json` directly if you prefer to craft entries by hand; ensure `file_name` paths are correct and point to files under the `albums/` directory.

## Project structure
Top-level layout (example tree) — this shows the expected project directory and the key files/folders the app uses:

```
albumized/
├─ app.py
├─ model.py
├─ search.py
├─ extract_album_covers.py
├─ metadata.json       # holds all of the metadata of albums inside database.
├─ faiss.index         # used for FAISS in closest neighbor search 
├─ test.py
├─ .env                # not committed; SECRET_KEY and optional Spotify creds
├─ albums/             # local album cover used to create embeddings 
│  ├─ cover_art_1.jpg
│  ├─ cover_art_2.jpg
│  └─ ...
├─ static/ 
│  ├─ styles.css
│  ├─ script.js
│  └─ images/          # images used in website 
│     ├─ question-mark-circle-icon.svg
│     └─ album_covers/     # Used for the creation of logo, along with items/
│        ├─ album_cover_1.jpg
│        └─ ...
└─ templates/          # main webpages 
  ├─ index.html
  └─ results.html
```

***Notes:**
- Make sure `albums/` and `metadata.json` exist before running the app.
- `faiss.index` must be present (or rebuilt) for search to work.
- FAISS install
  - If `pip install faiss-cpu` fails on macOS or Apple Silicon, use conda: `conda install -c conda-forge faiss-cpu`.

## Development notes
- The app serves thumbnails via `/cover/<faiss_index>` to avoid exposing arbitrary file paths.
- The search function returns metadata dictionaries from `metadata.json` and the template uses those fields (`name`, `artist`, `spotify_url`, `faiss_index`) to build result cards.

## Extending/Future updates
- Allow users to see similarity percentage using thresholding 
- More refined album results, potential upload to databse 
- Add server-side thumbnail generation to reduce image size.
- Add tests for `search.convert_img_to_embedding` and `find_k_similar`.
- Utilize another form of similarity search, such as cosine similarity rather than Euclidean

## License
MIT
