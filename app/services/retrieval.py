from typing import List, Tuple, Dict, Any, Optional
import re
import difflib
from app.db.vectorstore import VectorStore
from app.services.embedding import LocalEmbedder
from app.core.config import settings
from app.services.llm_providers import get_llm


# -------------------------------
# Utility scoring
# -------------------------------

def normalize_similarity_from_distance(distance: float) -> float:
    """
    Convert distance (various backends) to a 0..1 similarity.
    Handles both cosine and L2 distances.
    """
    try:
        dist = float(distance)
    except Exception:
        return 0.0
    if 0.0 <= dist <= 1.0:
        return 1.0 - dist
    return 1.0 / (1.0 + dist)


def keyword_score(query: str, text: str) -> float:
    query_words = set(re.findall(r"\w+", query.lower()))
    text_words = set(re.findall(r"\w+", text.lower()))
    if not query_words:
        return 0.0
    return len(query_words & text_words) / max(1, len(query_words))


def heading_boost(query: str, text: str) -> float:
    """
    Small boost if the query string appears as/at a heading or line start.
    """
    q = query.strip().lower()
    if not q:
        return 0.0
    for line in (l.strip().lower() for l in text.splitlines() if l.strip()):
        if q in line and (line.startswith(q) or line == q):
            return 0.5
    return 0.0


def extract_results(res) -> Tuple[List[str], List[dict], List[float]]:
    """
    Normalize vectorstore return shapes into (docs, metas, distances).
    """
    if isinstance(res, dict):
        docs = res.get("documents", [[]])
        metas = res.get("metadatas", [[]])
        distances = res.get("distances", [[]])
        if docs and isinstance(docs[0], list): docs = docs[0]
        if metas and isinstance(metas[0], list): metas = metas[0]
        if distances and isinstance(distances[0], list): distances = distances[0]
    elif isinstance(res, list):
        if len(res) == 3 and all(isinstance(x, list) for x in res):
            docs, metas, distances = res
        else:
            raise ValueError("Unexpected vectorstore query format")
    else:
        raise ValueError(f"Unexpected result type: {type(res)}")
    return docs, metas, distances


def _norm_text_for_dedupe(t: str) -> str:
    return " ".join((t or "").split())


def deduplicate_sources(sources: List[dict]) -> List[dict]:
    """
    Prefer dedupe by chunk_id; fallback to normalized text.
    """
    seen = {}
    for s in sources:
        cid = s.get("chunk_id")
        key = cid or _norm_text_for_dedupe(s["text"])
        if key not in seen or s["score"] > seen[key]["score"]:
            seen[key] = s
    return list(seen.values())


# -------------------------------
# Retrieval
# -------------------------------

def retrieve(query: str, top_k: Optional[int] = None, target_doc_id: Optional[str] = None) -> List[dict]:
    """
    Generic retrieval. Works for any document (no dataset-specific assumptions).
    Returns a ranked list of sources with fields:
      text, doc_id, page, chunk_id, score
    """
    embedder = LocalEmbedder(model_name=settings.embedding_model)
    query_embedding = embedder.embed_one(query)
    vs = VectorStore()

    # Scope to active document (or provided doc)
    doc_id = target_doc_id or vs.get_active_doc()
    if not doc_id:
        return []

    k_config = top_k or settings.top_k
    fetch_k = max(k_config * 10, 50)
    res = vs.query(query_embedding, where={"doc_id": doc_id}, top_k=fetch_k)

    docs, metas, distances = extract_results(res)
    sources: List[dict] = []

    for doc_text, metadata, dist in zip(docs, metas, distances):
        if not doc_text:
            continue

        similarity = normalize_similarity_from_distance(dist)
        kw_score = keyword_score(query, doc_text)
        fuzzy_score = difflib.SequenceMatcher(None, query.lower(), doc_text.lower()).ratio()
        boost = heading_boost(query, doc_text)

        # Combine scores (all generic)
        final_score = (0.65 * similarity) + (0.2 * kw_score) + (0.15 * fuzzy_score) + boost

        sources.append({
            "text": doc_text,
            "doc_id": (metadata or {}).get("doc_id"),
            "page": (metadata or {}).get("page"),
            "chunk_id": (metadata or {}).get("chunk_id"),
            "score": float(final_score),
        })

    sources.sort(key=lambda x: x["score"], reverse=True)
    sources = deduplicate_sources(sources)

    # Drop weak matches
    sources = [s for s in sources if s["score"] >= 0.25]

    # If very confident top match → keep only it
    if sources:
        top = sources[0]
        if top["score"] >= 0.85 and len(top["text"]) <= 600:
            return [top]

    return sources[:k_config]


# -------------------------------
# Answering
# -------------------------------

def _build_context(sources: List[dict], max_ctx_chunks: int) -> str:
    parts = []
    for idx, src in enumerate(sources[:max_ctx_chunks], start=1):
        page = src.get("page")
        prefix = f"[Source {idx}]" + (f" (page {page})" if page is not None else "")
        parts.append(f"{prefix} {src['text']}")
    return "\n\n".join(parts)


def _filter_sources_by_answer(answer: str, ranked_sources: List[dict]) -> List[dict]:
    """
    Keep only chunks that actually support the generated answer.
    Generic: uses overlap/fuzzy matching, no dataset-specific rules.
    """
    if not answer:
        return ranked_sources[:1] if ranked_sources else []

    ans_norm = " ".join(answer.lower().split())
    supporting: List[dict] = []

    for s in ranked_sources:
        text_norm = " ".join((s.get("text") or "").lower().split())
        if text_norm and (text_norm in ans_norm or ans_norm in text_norm):
            supporting.append(s)
            continue
        if difflib.SequenceMatcher(None, ans_norm, text_norm).ratio() >= 0.72:
            supporting.append(s)

    if supporting:
        supporting.sort(key=lambda x: x["score"], reverse=True)
        return supporting[:2]

    return ranked_sources[:1] if ranked_sources else []


def refine_answer(raw_answer: str) -> str:
    ans = (raw_answer or "").strip()
    if not ans:
        return "Not found in document."
    lowered = ans.lower()
    if lowered.startswith("not found") or "no relevant information" in lowered:
        return "Not found in document."
    return ans


def answer_with_context(query: str, sources: List[dict]):
    """
    Generate an answer using only retrieved context.
    Dataset-agnostic. If no relevant context, return "Not found in document."
    """
    if not sources:
        return "Not found in document.", []

    max_ctx = max(3, settings.top_k)
    context = _build_context(sources, max_ctx_chunks=max_ctx)

    prompt = f"""
You are a retrieval-based assistant.
Answer the question strictly using ONLY the provided context.
If the context is partially relevant, answer from it.
If the answer cannot be found in the context, reply exactly: "Not found in document."

Question:
{query}

Context:
{context}
""".strip()

    llm = get_llm()
    raw_answer = llm.generate(prompt)
    answer = refine_answer(raw_answer)

    supporting_sources = _filter_sources_by_answer(answer, sources)
    return answer, supporting_sources
