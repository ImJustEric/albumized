import os 
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from model import AlbumEmbeddingExtractor
import numpy as np 
from PIL import Image 

"""Input an query image and output an album whose cover is most similar to the image,
along with its metadata (artist, album name, etc)."""

def convert_img_to_embedding(img): 
    """Take an image (PIL.Image) or a filesystem path and run it through the pretrained model
    to produce its embeddings. Returns a 2-D numpy array suitable for FAISS search.
    """
    model = AlbumEmbeddingExtractor()

    # If a path was provided, open it. If a PIL Image was provided, use it directly.
    pil_img = None
    if isinstance(img, str):
        if not os.path.exists(img):
            print(f"Image does not exist at this path: {img}")
            return None
        try:
            pil_img = Image.open(img)
        except Exception as e:
            print(f"Failed to open image at path {img}: {e}")
            return None
    else:
        pil_img = img

    emb = model.embed_image(pil_img)
    emb = np.expand_dims(emb, axis=0) # Turn into 2-D vector 
    return emb 


def find_k_similar(img_emb, index, metadata, k) -> list[dict]:
    """Given a 2-D query embedding of an image, return the k most similar album covers and their
    metadata as a list of dictionary entries"""
    distances, indices = index.search(img_emb, k)
    distances = distances[0]
    indices = indices[0] # Only one search query 

    final_metadata = []

    for num in indices: 
        curr_metadata = metadata[num]
        final_metadata.append(curr_metadata)
    
    return final_metadata

def display_results(results): 
    """Input a list of metadata dicts and output the results"""
    for i, result in enumerate(results): 
        img = Image.open(result['file_name'])
        print(f"The number {i+1} most similar album to the input is {result['name']} by {result['artist'][0]}")
        img.show()





      