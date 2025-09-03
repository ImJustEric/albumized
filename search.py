import os 
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from model import AlbumEmbeddingExtractor
import numpy as np 
from PIL import Image 

"""Input an query image and output an album whose cover is most similar to the image,
along with its metadata (artist, album name, etc)."""

def convert_img_to_embedding(img): 
    """Take and image and run it through the pretrained model to product its embeddings"""
    if not img: 
        print(f"Image does not exist at this path: {img}")
        return 
    # Use a cached model instance to avoid loading the ResNet weights on every request
    model = get_model()
    emb = model.embed_image(img)
    emb = np.expand_dims(emb, axis=0) # Turn into 2-D vector 
    return emb 


# Singleton pattern to make sure only one Pytorch model is being loaded
_GLOBAL_MODEL = None
def get_model():
    global _GLOBAL_MODEL
    if _GLOBAL_MODEL is None:
        _GLOBAL_MODEL = AlbumEmbeddingExtractor()
    return _GLOBAL_MODEL


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





      