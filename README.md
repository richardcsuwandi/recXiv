# recXiv

![recXiv](https://github.com/richardcsuwandi/recXiv/blob/master/recxiv_logo.png)

recXiv is a **self-hostable semantic search engine** for arXiv papers. It is designed to run completely offline: embeddings are created with [Sentence-Transformers](https://www.sbert.net/) and stored in a local [FAISS](https://github.com/facebookresearch/faiss) index, so no external vector database or paid API calls are required.

## How it works
1. `data/build_index.py` reads the public `metadata.json`, embeds *title + abstract* with the `all-MiniLM-L6-v2` or `all-mpnet-base-v2` model, normalises the vectors and stores them in a `faiss.IndexFlatIP`.
2. The script writes two artefacts:
   * `data/faiss_index.bin` – the vector index
   * `data/metadata.json`  – a list with lightweight metadata for each paper.
3. `app/app.py` is a small Flask server that:
   * loads the index & metadata once at start-up,
   * exposes `/search?query=…` which returns the *k* most similar papers,
   * serves a minimal HTML/JS front-end.

## Quick start

Clone the repo and create a Python 3.10+ virtual environment:

```bash
git clone https://github.com/yourname/recXiv.git
cd recXiv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download the full arXiv metadata from [Kaggle](https://www.kaggle.com/datasets/Cornell-University/arxiv) and build an index:

```bash
python data/build_index.py \
  --arxiv-json path/to/metadata.json \
  --out-index data/faiss_index.bin \
  --out-meta  data/metadata.json
```

Adjust the `--max-papers` flag if you only want a subset.

## Configuration

The server can be tweaked with environment variables (all optional):

| variable             | default                     | description                          |
|----------------------|-----------------------------|--------------------------------------|
| RECXIV_INDEX_PATH    | `data/faiss_index.bin`      | path to the FAISS index file         |
| RECXIV_META_PATH     | `data/metadata.json`        | path to the metadata JSON            |
| RECXIV_EMBED_MODEL   | `all-MiniLM-L6-v2`          | sentence-transformer model to embed ad-hoc queries |
| RECXIV_TOP_K         | `10`                        | number of results to return          |
| RECXIV_USE_GPU       | `0`                         | set to `1` to move the index to GPU (Linux / CUDA build of FAISS) |

Example:

```bash
export RECXIV_TOP_K=5
export RECXIV_USE_GPU=1
gunicorn --bind 0.0.0.0:8000 app.app:app
```

## Docker

A minimal image can be built and run like so:

```bash
docker build -t recxiv-app ./app
docker run -p 8000:8000 \
  -v "$(pwd)/data":/app/data \
  recxiv-app
```
