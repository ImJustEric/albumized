import os 
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch 
import torch.nn as nn 
from torchvision import models, transforms
from PIL import Image
import numpy as np 
import faiss
import json

"""Use a pretrained ResNet50 model to create image embeddings for all album covers"""

class AlbumEmbeddingExtractor:
    def __init__(self):
        self._model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        self._model = nn.Sequential(*(list(self._model.children())[:-1])) # Remove last FC layer 

        # Switch to eval mode for embeddings 
        self._model.eval() 

        # NOTE: This assumes images are already formatted to 224x224 from extract_album_covers.py 
        self._transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
        ])
    

    def embed_image(self, img): 
        """Given an image, return its embedding"""
        # Check image size 
        if img.size != (224, 224):
            print("Image is not 224x224, transforming to correct size.")
            transform = transforms.Compose([
                transforms.Resize(224),        
                transforms.CenterCrop(224),     
            ])
            img = transform(img)
        img = img.convert("RGB")
        img_tensor = self._transform(img).unsqueeze(0)

        with torch.no_grad(): 
            embedding = self._model(img_tensor)
            embedding = embedding.squeeze().numpy()

        return embedding.astype("float32")

    def extract_embeddings(self, img_paths, metadata_path, index_path): 
        """Input a list of formatted image paths (size 224x224) and will save its image embeddings
        to an FAISS index. The index number of the embeddings will then be saved into its 
        corresponding metadata .json file.
        
        All args must be path names. Index_path will be the name of the index (whether it exists 
        or not )"""
        # Check if index exists 
        if os.path.exists(index_path): 
            index = faiss.read_index(index_path)
        else: 
            index = faiss.IndexFlatL2(2048) # 2048 is size of vector from ResNet50 

        # Check if json exists 
        if not os.path.exists(metadata_path): 
            print("Metadata json file does not exist!")
            return 

        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        # Build map for metadata to find entry later 
        metadata_hash = {album["file_name"]: album for album in metadata}

        for img_path in img_paths: 
            img = Image.open(img_path)
            emb = self.embed_image(img)
            print(f"Successfully embedded image {img_path}")
            # Save embedding into index 
            index.add(np.expand_dims(emb, axis=0))
            print(f"Successfully added {img_path} to index")
            # Find the entry by file_name and update faiss_index
            metadata_hash[img_path]["faiss_index"] = index.ntotal - 1

        # Save metadata 
        with open(metadata_path, "w") as f: 
            json.dump(list(metadata_hash.values()), f, indent=4)

        # Save index
        faiss.write_index(index, index_path)

