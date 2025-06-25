"""build_index.py
Create a FAISS index and metadata file for a minimal recXiv deployment.

Usage (once you have downloaded the Kaggle arXiv metadata):
    python build_index.py \
        --arxiv-json path/to/arxiv-metadata-oai-snapshot.json \
        --out-index data/faiss_index.bin \
        --out-meta  data/metadata.json

This script will
1. filter papers to primary categories cs.AI and cs.LG
2. use SentenceTransformers to embed "title + abstract"
3. normalise embeddings and store them in a FAISS IndexFlatIP
4. write the index and a metadata JSON list to disk.

The resulting files are loaded by the Flask app at runtime.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

CATEGORIES = {"cs.ai", "cs.lg", "cs.cv", "cs.cl", "cs.ne"}
MODEL_NAME = "all-MiniLM-L6-v2"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arxiv-json", required=True, type=Path,
                        help="Path to arxiv-metadata-oai-snapshot.json")
    parser.add_argument("--out-index", default=Path("data/faiss_index.bin"), type=Path)
    parser.add_argument("--out-meta", default=Path("data/metadata.json"), type=Path)
    parser.add_argument("--max-papers", type=int, default=None,
                        help="Optional limit for debugging.")
    return parser.parse_args()


def iter_papers(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def filter_paper(j: dict) -> bool:
    cats = set(j["categories"].lower().split())
    # keep if primary (first) category is in target list
    primary = list(cats)[0] if cats else ""
    return primary in CATEGORIES


def build_metadata_entry(j: dict) -> dict:
    # Title & abstract cleanup
    title = " ".join(j["title"].strip().split())
    abstract = " ".join(j["abstract"].strip().split())
    year = int(j["versions"][0]["created"].split()[3])
    month = j["versions"][0]["created"].split()[2]

    authors_parsed = j["authors_parsed"]
    authors = [" ".join(a[::-1][1:]).strip() for a in authors_parsed]
    authors_string = ", ".join(authors)

    # Get categories and clean them up
    categories = j["categories"].lower().split()

    return {
        "id": j["id"],
        "title": title,
        "authors": authors_string,
        "abstract": abstract,
        "year": year,
        "month": month,
        "categories": categories  # Add categories to metadata
    }


def main():
    args = parse_args()

    model = SentenceTransformer(MODEL_NAME)
    metadata: List[dict] = []
    vectors: List[np.ndarray] = []

    for j in tqdm(iter_papers(args.arxiv_json), desc="Filtering & embedding"):
        if not filter_paper(j):
            continue
        entry = build_metadata_entry(j)
        vec = model.encode(entry["title"] + ". " + entry["abstract"], normalize_embeddings=True)
        metadata.append(entry)
        vectors.append(vec)
        if args.max_papers and len(metadata) >= args.max_papers:
            break

    vectors_np = np.vstack(vectors).astype("float32")
    dim = vectors_np.shape[1]

    index = faiss.IndexFlatIP(dim)

    # optional GPU accelerate for Linux/NVIDIA with faiss-gpu installed
    try:
        gpu = args.out_index.suffix == ".gpu"  # simple flag by output name
        if gpu and faiss.get_num_gpus() > 0 and faiss.StandardGpuResources is not None:
            res = faiss.StandardGpuResources()
            gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
            gpu_index.add(vectors_np)
            index_cpu = faiss.index_gpu_to_cpu(gpu_index)
            index = index_cpu
        else:
            index.add(vectors_np)
    except AttributeError:
        index.add(vectors_np)  # fallback

    args.out_index.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(args.out_index))

    with open(args.out_meta, "w") as f:
        json.dump(metadata, f)

    print(f"✅ Built index with {index.ntotal} papers → {args.out_index}")
    print(f"✅ Wrote metadata → {args.out_meta}")


if __name__ == "__main__":
    main() 