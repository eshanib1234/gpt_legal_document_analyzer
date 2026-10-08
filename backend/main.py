"""
main.py
=======
FastAPI application backend for the Automated Legal Document Analyzer.
Provides endpoints for document analysis, health check, and sample document retrieval.
All analysis runs locally using Ollama (no OpenAI / external APIs).
"""

import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from ollama_service import check_ollama_status, DEFAULT_MODEL
from document_processor import process_and_analyze_document

# Initialize FastAPI App
app = FastAPI(
    title="Automated Legal Document Analyzer",
    description="Laboratory Experiment 5: Analyzing legal contracts locally using Ollama & Llama 3.2",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite defaults to 5173, fallback 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits requests from frontend running on any local port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Request Models
class AnalyzeRequest(BaseModel):
    document_text: str = Field(..., description="The raw legal document text to be analyzed")
    model_name: Optional[str] = Field(default=DEFAULT_MODEL, description="Ollama model name to use")


@app.get("/")
def read_root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "project": "Automated Legal Document Analyzer",
        "experiment": "Experiment 5: Ollama Local LLM Legal Document Extraction",
        "backend": "FastAPI",
        "status": "online",
        "endpoints": {
            "health": "GET /health",
            "sample": "GET /sample",
            "analyze": "POST /analyze"
        }
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint: verifies backend status and checks if local Ollama
    is active and the llama3.2:latest model is available.
    """
    ollama_info = check_ollama_status()
    
    return {
        "status": "ok" if ollama_info["running"] else "degraded",
        "ollama": ollama_info["running"],
        "model": ollama_info["actual_model"] or DEFAULT_MODEL,
        "model_available": ollama_info["model_available"],
        "available_models": ollama_info["available_models"],
        "pull_command": ollama_info["pull_command"],
        "message": ollama_info["message"]
    }


@app.get("/sample")
def get_sample_document():
    """
    Returns the standard sample Employment Agreement used for laboratory testing.
    """
    sample_path = os.path.join(os.path.dirname(__file__), "sample_document.txt")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            content = f.read()
            return {"sample_text": content}
    
    # Fallback default sample text if file is missing
    fallback_text = """EMPLOYMENT AGREEMENT

This Employment Agreement is between ABC Technologies Pvt. Ltd. and John Smith.

The employee will work as a Software Developer.

The employment period is 12 months starting from 01-07-2026.

The employee will receive a monthly salary of ₹50,000.

The employee must maintain confidentiality regarding company information.

The employee must perform assigned duties and follow company policies.

Either party may terminate the agreement by providing 30 days written notice.

Any intellectual property created during employment belongs to the company.

The agreement is governed by the applicable laws of India."""
    return {"sample_text": fallback_text}


@app.post("/analyze")
def analyze_document_endpoint(payload: AnalyzeRequest):
    """
    Main analysis endpoint.
    Accepts legal document text, validates it, preprocesses & chunks if necessary,
    queries the local Ollama LLM, and returns structured JSON analysis.
    """
    if not payload.document_text or not payload.document_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text cannot be empty. Please provide text to analyze."
        )

    # First verify Ollama is alive
    health = check_ollama_status(payload.model_name or DEFAULT_MODEL)
    if not health["running"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama is not running. Please start Ollama using 'ollama serve' and try again."
        )

    # Process and analyze the document
    success, analysis_result, metadata, error_msg = process_and_analyze_document(
        raw_text=payload.document_text,
        model_name=payload.model_name or DEFAULT_MODEL
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg or "Failed to analyze document with Ollama."
        )

    return {
        "success": True,
        "analysis": analysis_result,
        "metadata": metadata
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
