"""
document_processor.py
=====================
Handles document preprocessing, validation, chunking, and multi-chunk result merging.
Keeps implementation simple, transparent, and educational for lab experiments.
"""

import re
from typing import List, Dict, Any, Tuple
from ollama_service import query_ollama_analyze, DEFAULT_SCHEMA_KEYS

# Threshold for document chunking (characters)
# Approximately 2500 characters (~500 words) per chunk for optimal local LLM context
CHUNK_SIZE_THRESHOLD = 3000
MAX_CHUNK_CHARS = 2500


def preprocess_text(text: str) -> str:
    """
    Cleans raw document text by standardizing line breaks and stripping excessive whitespace.
    """
    if not text:
        return ""
    # Normalize Windows CRLF to standard LF
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace sequences of 3 or more newlines with double newline
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def is_valid_document(text: str) -> Tuple[bool, str]:
    """
    Validates whether the document input is suitable for legal analysis.
    """
    cleaned = preprocess_text(text)
    if not cleaned:
        return False, "Document text is empty. Please provide legal text or upload a document."
    
    if len(cleaned.split()) < 5:
        return False, "Document is too short for meaningful legal analysis (minimum 5 words)."
    
    return True, ""


def split_into_chunks(text: str, max_chars: int = MAX_CHUNK_CHARS) -> List[str]:
    """
    Splits a long legal document into logical chunks based on paragraphs or sentences.
    Ensures that clauses are not abruptly cut in the middle of sentences.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            continue
        
        para_len = len(para_clean)
        
        # If single paragraph is itself excessively long, split by sentences
        if para_len > max_chars:
            sentences = re.split(r"(?<=[.!?])\s+", para_clean)
            for sentence in sentences:
                sent_len = len(sentence)
                if current_length + sent_len + 1 > max_chars and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [sentence]
                    current_length = sent_len
                else:
                    current_chunk.append(sentence)
                    current_length += sent_len + 1
        elif current_length + para_len + 2 > max_chars and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para_clean]
            current_length = para_len
        else:
            current_chunk.append(para_clean)
            current_length += para_len + 2

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks if chunks else [text]


def merge_chunk_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges structured analysis results from multiple chunks into a unified JSON document.
    Deduplicates list items (parties, obligations, dates, clauses) and summarizes text fields.
    """
    if not results:
        return {}

    if len(results) == 1:
        return results[0]

    merged: Dict[str, Any] = {}
    
    # List fields: collect unique non-placeholder items
    list_fields = [
        "parties", "obligations", "rights", 
        "important_dates", "key_clauses", "potentially_important_clauses"
    ]
    
    for key in list_fields:
        combined_list = []
        seen = set()
        for res in results:
            items = res.get(key, [])
            if isinstance(items, list):
                for item in items:
                    item_str = str(item).strip()
                    if item_str and item_str != "Not specified in the document." and item_str.lower() not in seen:
                        seen.add(item_str.lower())
                        combined_list.append(item_str)
        merged[key] = combined_list if combined_list else ["Not specified in the document."]

    # String fields: pick first well-defined non-placeholder value or synthesize
    string_fields = [
        "document_type", "purpose", "payment_terms", 
        "duration", "termination", "confidentiality", "governing_law"
    ]
    for key in string_fields:
        chosen_val = "Not specified in the document."
        for res in results:
            val = str(res.get(key, "")).strip()
            if val and val != "Not specified in the document.":
                chosen_val = val
                break
        merged[key] = chosen_val

    # Summaries: combine distinct summaries
    summaries = []
    for idx, res in enumerate(results):
        summary_text = str(res.get("summary", "")).strip()
        if summary_text and summary_text != "Not specified in the document.":
            summaries.append(summary_text)
    
    if summaries:
        merged["summary"] = " ".join(summaries)
    else:
        merged["summary"] = "Not specified in the document."

    return merged


def process_and_analyze_document(raw_text: str, model_name: str = "llama3.2:latest") -> Tuple[bool, Dict[str, Any], Dict[str, Any], str]:
    """
    Orchestrates the complete document analysis pipeline:
    1. Validation
    2. Preprocessing
    3. Chunk determination
    4. Inference via Ollama
    5. Result synthesis

    Returns: (success: bool, analysis_data: dict, metadata: dict, error_message: str)
    """
    valid, err_msg = is_valid_document(raw_text)
    if not valid:
        return False, {}, {}, err_msg

    cleaned_text = preprocess_text(raw_text)
    char_count = len(cleaned_text)
    word_count = len(cleaned_text.split())

    # Decide if chunking is needed
    if char_count > CHUNK_SIZE_THRESHOLD:
        chunks = split_into_chunks(cleaned_text)
        is_chunked = True
    else:
        chunks = [cleaned_text]
        is_chunked = False

    metadata = {
        "character_count": char_count,
        "word_count": word_count,
        "is_chunked": is_chunked,
        "chunk_count": len(chunks)
    }

    chunk_results = []
    for i, chunk in enumerate(chunks):
        success, res_json, err = query_ollama_analyze(chunk, model_name)
        if not success:
            return False, {}, metadata, f"Analysis failed at chunk {i+1}/{len(chunks)}: {err}"
        chunk_results.append(res_json)

    final_analysis = merge_chunk_results(chunk_results)
    return True, final_analysis, metadata, ""
