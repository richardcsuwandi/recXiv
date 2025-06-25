import json
from collections import defaultdict
from app.paper import Paper

# ---------------------------------------------------------------------------
# Utility functions used by the Flask app
# ---------------------------------------------------------------------------

def avg_score(papers):
    """Average similarity score over a list of `Paper` objects."""
    return round(sum(p.score for p in papers) / len(papers), 2) if papers else 0.0


def get_authors(papers):
    """Aggregates papers per author and computes their average score."""
    authors = defaultdict(list)
    for paper in papers:
        for author in paper.authors_parsed:
            authors[author].append(paper)

    authors_summary = []
    for author, authored_papers in authors.items():
        authors_summary.append({
            "author": author,
            "papers": [p.__dict__ for p in authored_papers],
            "avg_score": avg_score(authored_papers)
        })

    # sort by number of matching papers (desc)
    authors_summary.sort(key=lambda e: len(e["papers"]), reverse=True)
    return authors_summary[:10]


def build_response(matches, max_results: int = 10):
    """Converts raw match dictionaries to the JSON structure expected by the UI."""
    paper_objects = [Paper(m) for m in matches[:max_results]]
    authors = get_authors(paper_objects)
    papers = [p.__dict__ for p in paper_objects]
    return json.dumps({"papers": papers, "authors": authors})


def error(msg):
    """Returns an error JSON with the given message."""
    return json.dumps({"error": msg})
