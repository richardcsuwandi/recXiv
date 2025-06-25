class Paper(dict):
    def __init__(self, match):
        super().__init__()
        
        self.id = match["id"]
        self.score = round(match["score"], 2)
        
        metadata = match["metadata"]
        self.title = metadata["title"]
        self.authors = metadata["authors"]
        self.abstract = metadata["abstract"]
        self.year = metadata["year"]
        self.month = metadata["month"]
        self.categories = metadata.get("categories", [])  # Make categories optional with default empty list
        
        authors_parsed = self.authors.split(",")
        self.authors_parsed = [author.strip() for author in authors_parsed]
        
        # Convert to dict for JSON serialization
        self.update({
            "id": self.id,
            "score": self.score,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "year": self.year,
            "month": self.month,
            "categories": self.categories
        })