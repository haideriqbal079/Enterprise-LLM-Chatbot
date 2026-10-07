from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = PROJECT_ROOT / "docs" / "knowledge"


def parse_frontmatter(content: str):
    metadata = {}

    if not content.startswith("---"):
        return metadata, content

    parts = content.split("---", 2)

    if len(parts) < 3:
        return metadata, content

    frontmatter = parts[1].strip()
    body = parts[2].strip()

    for line in frontmatter.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata, body


def load_documents():
    documents = []

    for file_path in KNOWLEDGE_DIR.rglob("*.md"):
        content = file_path.read_text(encoding="utf-8")

        metadata, body = parse_frontmatter(content)

        documents.append(
            {
                "path": str(file_path),
                "metadata": metadata,
                "content": body,
            }
        )

    return documents


def search_documents(query: str, limit: int = 3):
    stop_words = {
        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
        "is",
        "are",
        "was",
        "were",
        "the",
        "a",
        "an",
        "of",
        "does",
        "do",
        "did",
        "to",
        "for",
        "in",
        "on",
        "at",
        "and",
        "or",
        "have",
        "has",
        "their",
        "its",
    }

    query_words = {
        word.strip(".,?!:;()[]{}'\"").lower()
        for word in query.split()
        if len(word.strip(".,?!:;()[]{}'\"")) > 2
        and word.strip(".,?!:;()[]{}'\"").lower() not in stop_words
    }

    query_lower = query.lower()

    documents = load_documents()
    scored_documents = []

    intent_rules = [
        (
            ["uk headquarters", "united kingdom headquarters", "uk head office"],
            ["united kingdom headquarters", "uk headquarters"],
        ),
        (
            ["employees", "employee", "company size", "how many employees"],
            ["company size", "employees"],
        ),
        (
            ["director"],
            ["director"],
        ),
        (
            ["chairman"],
            ["chairman"],
        ),
        (
            ["customers", "customer", "clients", "client"],
            ["customers", "clients", "customer types"],
        ),
        (
            ["products", "product", "solutions", "solution"],
            ["products", "solutions", "saas"],
        ),
        (
            ["working days", "standard working days"],
            ["monday", "friday", "working hours"],
        ),
    ]

    for document in documents:
        title = document["metadata"].get("title", "").lower()
        description = document["metadata"].get("description", "").lower()
        content = document["content"].lower()

        score = 0

        # Basic keyword matching
        for word in query_words:
            if word in title:
                score += 5

            if word in description:
                score += 3

            if word in content:
                score += 1

        # Exact phrase matching
        for phrase in query_words:
            if phrase in content:
                score += 4

        # Query-intent matching
        for triggers, target_phrases in intent_rules:
            if any(trigger in query_lower for trigger in triggers):
                for target in target_phrases:
                    if target in content:
                        score += 12

                    if target in title:
                        score += 6

        # Existing high-priority rules
        if "founded" in query_lower and "founded" in content:
            score += 10

        if "ceo" in query_lower and "ceo" in content:
            score += 10

        if "working hours" in query_lower and "working hours" in content:
            score += 10

        if "pakistan office" in query_lower and "pakistan office" in content:
            score += 10

        scored_documents.append((score, document))

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        document
        for score, document in scored_documents[:limit]
        if score > 0
    ]