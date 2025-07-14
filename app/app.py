import os
import json
from typing import List

import flask
from flask import render_template, request
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import validators
import torch

from app.helpers import build_response, error

app = flask.Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEVICE = "cpu"  # Force CPU for Vercel deployment
MAX_QUERY_LEN = 200  # characters
TOP_K = 10
DATA_PATH = "data/minilm" # data/mpnet or data/minilm
INDEX_PATH = DATA_PATH + "/faiss_index.gpu"
META_PATH = DATA_PATH + "/metadata.json"
if DATA_PATH == "data/mpnet":
    EMBEDDING_MODEL = "all-mpnet-base-v2"
else:
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
print("[recXiv] loading sentence-transformer model ...", flush=True)
model = SentenceTransformer(EMBEDDING_MODEL, device=DEVICE)
print("[recXiv] loading faiss index ...", flush=True)
index = faiss.read_index(INDEX_PATH)
print("[recXiv] reading metadata ...", flush=True)
with open(META_PATH, "r") as f:
    metadata: List[dict] = json.load(f)

assert len(metadata) == index.ntotal, (
    "Index size and metadata size mismatch: "
    f"{index.ntotal} vs {len(metadata)}"
)
print(f"[recXiv] ready — {index.ntotal} papers indexed.", flush=True)

# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/search")
def search():
    query = request.args.get("query", "").strip()

    if not query:
        return error("Please provide a non-empty query.")
    
    # natural language query length guard
    if len(query) > MAX_QUERY_LEN:
        return error("Sorry! The length of your query cannot exceed 200 characters.")
    
    # if user pasted an arXiv URL, try to fetch its abstract and embed
    if validators.url(query) and "arxiv.org" in query:
        arxiv_id = query.split("/")[-1]
        # look up local metadata first
        id_to_meta = {m["id"]: m for m in metadata}
        if arxiv_id in id_to_meta:
            query_vec = get_vector_for_id(id_to_meta[arxiv_id])
        else:
            # fallback to using the url as text if id unknown
            query_vec = encode_query(query)
    else:
        query_vec = encode_query(query)

    # search in faiss
    scores, idxs = index.search(query_vec, TOP_K)
    matches = []
    for i, s in zip(idxs[0], scores[0]):
        meta = metadata[i]
        matches.append({
            "id": meta["id"],
            "score": float(round(s, 2)),
            "metadata": meta
        })

    return build_response(matches)


@app.route("/robots.txt")
def robots():
    with open("static/robots.txt", "r") as f:
        content = f.read()
    return content


# ---------------------------------------------------------------------------
# Helper functions internal to this module
# ---------------------------------------------------------------------------

def encode_query(text: str) -> np.ndarray:
    vec = model.encode([text], normalize_embeddings=True)
    return np.array(vec).astype("float32")


def get_vector_for_id(meta: dict) -> np.ndarray:
    """Encodes a paper's title + abstract to reuse the same embedding space."""
    text = meta.get("title", "") + ". " + meta.get("abstract", "")
    return encode_query(text)
