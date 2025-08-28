import os
from dotenv import load_dotenv
load_dotenv()
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import spotipy
from spotipy.oauth2 import SpotifyOAuth 
import requests
from PIL import Image
from io import BytesIO
from torchvision import transforms
import json 

"""Extract the album cover arts from certain artists and specific input albums
and format the files to a size applicable for ResNet."""

"""NOTE: If you want to delete album images, make sure you delete metadata as well"""

BASE_DIR = os.path.dirname(__file__) # Configure the base directory 
 
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    cache_path=".spotipyoauthcache"
))

# Extract albums from artists 
artists = [
    "3TVXtAsR1Inumwj472S9r4", # Drake
    "06HL4z0CvFAxyc27GXpf02", # Taylor Swift
    "246dkjvS1zLTtiykXe5h60", # Post Malone 
    "7eKkW1zo5uzW8kUntiiBvz", # Malcolm Todd
    "40ZNYROS4zLfyyBSs2PGe2", # Zach Bryan
    "7tYKF4w9nC0nq9CsPZTHyP" # SZA
]

def get_albums(artist_id): 
    """Return a list of Spotipy album dictionaries created by an artist.
    Doing so will keep the metadata associated with the album."""
    results = sp.artist_albums(artist_id, album_type="album", limit=20)
    albums = results['items']

    # Get rid of any duplicate albums or deluxe albums 
    seen = set() 
    final = []

    for album in albums: 
        album_name = album['name'].lower()
        if album_name not in seen: 
            seen.add(album_name)
            final.append(album)
    
    return final 


def get_album_art(album, file_name):
    "Given an album dictionary, save the album cover art as a jpg and its metadata into a .json file"
    images = album["images"]

    if not images:
        print(f"No cover art found for this album id: {album['id']}")
        return
    
    cover_url = images[0]["url"]

    # Download image
    response = requests.get(cover_url)
    if response.status_code == 200:
        # Resize the photo 
        img = Image.open(BytesIO(response.content))

        # Resize shortest side to 224, then crop to 224x224
        transform = transforms.Compose([
            transforms.Resize(224),        
            transforms.CenterCrop(224),     
        ])

        img_resized = transform(img)

        img_resized.save(file_name, "JPEG")
        print(f"Saved resized cover art (224x224) to {file_name}")
        return 0 
    else:
        print(f"Failed to download cover art: {response.status_code}")
        return 


if __name__ == "__main__":
    # Folder path directory 
    album_dir = os.path.join(BASE_DIR, 'albums')
    metadata_file = os.path.join(BASE_DIR, 'metadata.json')

    # Check if album folder exists: 
    os.makedirs(album_dir, exist_ok=True)

    # Check if metadata exists, else metadata array does not exist and is empty 
    if os.path.exists(metadata_file): 
        with open(metadata_file, "r") as f: 
            metadata = json.load(f)
            count = len(metadata) + 1
    else: 
        metadata = []
        count = 1

    for artist in artists: 
        albums = get_albums(artist)
        for album in albums: 
            img_file = f"cover_art_{count}.jpg"
            file_path = os.path.join(album_dir, img_file)
            get_album_art(album=album, file_name=file_path)


            metadata_ex = {
            "file_name": file_path,
            "id": album["id"],
            "name": album["name"],
            "release_date": album["release_date"],
            "total_tracks": album["total_tracks"],
            "artist": [artist["name"] for artist in album["artists"]],
            "spotify_url": album["external_urls"]["spotify"],
            "faiss_index": None
            }

            metadata.append(metadata_ex)
            count += 1
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Updated {metadata_file} with {len(metadata)} albums total")
