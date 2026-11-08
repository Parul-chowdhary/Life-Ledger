"""
Search Indexing & Phonetic Retrieval Engine.
Implements Soundex phonetic hashing, BM25-style inverted indexing,
and tenant-isolated multi-field document search.
"""
from collections import defaultdict
import math
import re
from typing import Any, Dict, List, Optional, Set


def soundex(word: str) -> str:
    """Generates a 4-character American Soundex phonetic hash code."""
    if not word:
        return "0000"
    word = re.sub(r"[^A-Za-z]", "", word).upper()
    if not word:
        return "0000"

    first_letter = word[0]
    mapping = {
        "B": "1", "F": "1", "P": "1", "V": "1",
        "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
        "D": "3", "T": "3",
        "L": "4",
        "M": "5", "N": "5",
        "R": "6"
    }

    encoded = [first_letter]
    prev_code = mapping.get(first_letter, "")

    for char in word[1:]:
        code = mapping.get(char, "")
        if code and code != prev_code:
            encoded.append(code)
            prev_code = code
        elif not code:
            prev_code = ""

    # Pad with zeros or truncate to length 4
    result = "".join(encoded)
    return (result + "0000")[:4]


class InvertedIndex:
    """High-performance in-memory inverted index with TF-IDF scoring."""

    def __init__(self):
        # term -> {doc_id: term_frequency}
        self.index: Dict[str, Dict[str, int]] = defaultdict(dict)
        # phonetic_code -> {doc_id}
        self.phonetic_index: Dict[str, Set[str]] = defaultdict(set)
        # doc_id -> total terms
        self.doc_lengths: Dict[str, int] = {}
        # doc_id -> {field: value}
        self.documents: Dict[str, Dict[str, Any]] = {}

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b[A-Za-z0-9_-]{2,}\b", text)]

    def add_document(self, doc_id: str, fields: Dict[str, Any]) -> None:
        self.documents[doc_id] = fields
        all_text = " ".join(str(v) for v in fields.values())
        tokens = self._tokenize(all_text)
        self.doc_lengths[doc_id] = len(tokens)

        # Count frequencies
        tf_counts: Dict[str, int] = defaultdict(int)
        for t in tokens:
            tf_counts[t] += 1
            # Add phonetic soundex entry for alphabetic terms
            if t.isalpha():
                self.phonetic_index[soundex(t)].add(doc_id)

        for term, count in tf_counts.items():
            self.index[term][doc_id] = count

    def remove_document(self, doc_id: str) -> None:
        if doc_id in self.documents:
            del self.documents[doc_id]
        if doc_id in self.doc_lengths:
            del self.doc_lengths[doc_id]
        for term in list(self.index.keys()):
            if doc_id in self.index[term]:
                del self.index[term][doc_id]

    def search(self, query: str, workspace_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores: Dict[str, float] = defaultdict(float)
        total_docs = max(1, len(self.documents))

        for qt in query_tokens:
            # 1. Exact term matches
            if qt in self.index:
                postings = self.index[qt]
                df = len(postings)
                idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
                for doc_id, tf in postings.items():
                    doc_len = self.doc_lengths.get(doc_id, 50)
                    score = (tf * (2.2)) / (tf + 1.2 * (0.25 + 0.75 * (doc_len / 50)))
                    scores[doc_id] += score * idf

            # 2. Phonetic matches if alphabetic
            if qt.isalpha():
                sx = soundex(qt)
                for doc_id in self.phonetic_index.get(sx, set()):
                    scores[doc_id] += 0.45  # Boost for phonetic similarity

        # Filter by workspace if provided
        results = []
        for doc_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            doc = self.documents.get(doc_id)
            if doc:
                if workspace_id and doc.get("workspace_id") != workspace_id:
                    continue
                results.append({
                    "id": doc_id,
                    "doc_id": doc_id,
                    "score": round(score, 3),
                    "document": doc,
                })
                if len(results) >= limit:
                    break

        return results
