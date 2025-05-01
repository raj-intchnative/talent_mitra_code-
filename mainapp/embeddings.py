# embeddings.py

from vertexai.language_models import TextEmbeddingModel

def get_text_embedding(text):
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")
    embedding = model.get_embeddings([text])[0].values
    return embedding  # returns a list of floats
