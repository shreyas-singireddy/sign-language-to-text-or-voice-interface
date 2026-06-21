import math
import re
from pathlib import Path

from config.logger import setup_logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

logger = setup_logger("ai_agent.rag")

DOCS_DIR = PROJECT_ROOT / "PROJECT_MASTER_DOCUMENTATION"

# Simple list of English stop words to filter out during indexing
STOP_WORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "arent",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "cant",
    "cannot",
    "could",
    "did",
    "didnt",
    "do",
    "does",
    "doesnt",
    "doing",
    "dont",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadnt",
    "has",
    "hasnt",
    "have",
    "havent",
    "having",
    "he",
    "hed",
    "hell",
    "hes",
    "her",
    "here",
    "heres",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "hows",
    "i",
    "id",
    "ill",
    "im",
    "ive",
    "if",
    "in",
    "into",
    "is",
    "isnt",
    "it",
    "its",
    "itself",
    "lets",
    "me",
    "more",
    "most",
    "mustnt",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "shant",
    "she",
    "shed",
    "shell",
    "shes",
    "should",
    "shouldnt",
    "so",
    "some",
    "such",
    "than",
    "that",
    "thats",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "theres",
    "these",
    "they",
    "theyd",
    "theyll",
    "theyre",
    "theyve",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "wasnt",
    "we",
    "wed",
    "well",
    "were",
    "weve",
    "werent",
    "what",
    "whats",
    "when",
    "whens",
    "where",
    "wheres",
    "which",
    "while",
    "who",
    "whos",
    "whom",
    "why",
    "whys",
    "with",
    "wont",
    "would",
    "wouldnt",
    "you",
    "youd",
    "youll",
    "youre",
    "youve",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


def tokenize(text: str) -> list:
    """Lowercase and extract words from text."""
    words = re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())
    return [w for w in words if w not in STOP_WORDS]


class RAGEngine:
    def __init__(self):
        self.chunks = []  # List of dict: {"file": str, "content": str, "title": str}
        self.idf = {}  # Vocabulary IDF mapping
        self.chunk_vectors = []  # List of dict mappings: {word: tf_idf}
        self.indexed = False

    def load_and_index(self):
        """Scans project documentation and builds a TF-IDF index over chunks."""
        if not DOCS_DIR.exists():
            logger.warning(f"Documentation directory {DOCS_DIR} not found. RAG search disabled.")
            return

        self.chunks = []
        logger.info(f"Indexing Markdown files in {DOCS_DIR}...")

        for file_path in DOCS_DIR.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                # Split file into chunks by secondary headings (##) or blocks of text
                sections = re.split(r"(?=^##\s+)", content, flags=re.MULTILINE)

                for sec in sections:
                    sec_clean = sec.strip()
                    if len(sec_clean) < 50:
                        continue  # skip tiny snippets

                    # Extract heading title if any
                    title_match = re.match(r"^##\s+(.+)$", sec_clean, re.MULTILINE)
                    title = title_match.group(1).strip() if title_match else file_path.name

                    self.chunks.append({"file": file_path.name, "title": title, "content": sec_clean})
            except Exception as e:
                logger.error(f"Failed to read file {file_path.name}: {e}")

        # Compute TF-IDF
        num_docs = len(self.chunks)
        if num_docs == 0:
            logger.warning("No document chunks loaded for index.")
            return

        # Count document frequency (DF) for each word
        df = {}
        for chunk in self.chunks:
            tokens = set(tokenize(chunk["content"]))
            for t in tokens:
                df[t] = df.get(t, 0) + 1

        # Compute IDF
        self.idf = {}
        for word, count in df.items():
            self.idf[word] = math.log((num_docs + 1) / (count + 1)) + 1.0

        # Build chunk vectors
        self.chunk_vectors = []
        for chunk in self.chunks:
            tokens = tokenize(chunk["content"])
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1

            vector = {}
            for word, count in tf.items():
                # tf-idf = count * idf
                vector[word] = count * self.idf.get(word, 0.0)
            self.chunk_vectors.append(vector)

        self.indexed = True
        logger.info(f"Successfully indexed {num_docs} document chunks.")

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieves top K documentation chunks matching the query string."""
        if not self.indexed:
            self.load_and_index()

        query_tokens = tokenize(query)
        if not query_tokens or not self.chunks:
            return ""

        # Compute query vector
        query_vector = {}
        for t in query_tokens:
            query_vector[t] = query_vector.get(t, 0) + 1
        for word in list(query_vector.keys()):
            query_vector[word] = query_vector[word] * self.idf.get(word, 0.0)

        # Compute cosine similarities
        scores = []
        for idx, chunk_vector in enumerate(self.chunk_vectors):
            dot_product = 0.0
            query_norm = 0.0
            chunk_norm = 0.0

            # Since query vector is small, iterate over it
            for word, val in query_vector.items():
                if word in chunk_vector:
                    dot_product += val * chunk_vector[word]

            query_norm = math.sqrt(sum(val**2 for val in query_vector.values()))
            chunk_norm = math.sqrt(sum(val**2 for val in chunk_vector.values()))

            score = 0.0
            if query_norm > 0 and chunk_norm > 0:
                score = dot_product / (query_norm * chunk_norm)

            scores.append((score, idx))

        # Sort and select top K chunks
        scores.sort(reverse=True, key=lambda x: x[0])
        results = []

        for score, idx in scores[:top_k]:
            if score > 0.05:  # relevance threshold
                chunk = self.chunks[idx]
                results.append(f"--- Source: {chunk['file']} (Section: {chunk['title']}) ---\n" f"{chunk['content']}")

        return "\n\n".join(results)


rag_engine = RAGEngine()
