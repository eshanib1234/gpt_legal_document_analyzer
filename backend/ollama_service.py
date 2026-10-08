"""
ollama_service.py
=================
Handles communication with the local Ollama LLM service via HTTP REST API.
No external API keys or OpenAI dependencies are used.
"""

import json
import re
import requests
from typing import Dict, Any, Tuple

# Default local Ollama URL and Model
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:latest"

# Standard template for the analysis result
DEFAULT_SCHEMA_KEYS = [
    "document_type",
    "parties",
    "purpose",
    "obligations",
    "rights",
    "payment_terms",
    "duration",
    "termination",
    "confidentiality",
    "important_dates",
    "governing_law",
    "key_clauses",
    "potentially_important_clauses",
    "summary"
]


def check_ollama_status(target_model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Checks if the local Ollama service is reachable and if the required model is installed.
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            
            # Check if target model (e.g. llama3.2:latest or llama3.2) is available
            model_found = any(
                target_model in m or m.startswith(target_model.split(":")[0]) 
                for m in models
            )
            
            # Find the actual matching model name
            actual_model = target_model if model_found else (models[0] if models else "")

            return {
                "running": True,
                "model_available": model_found,
                "target_model": target_model,
                "actual_model": actual_model,
                "available_models": models,
                "pull_command": f"ollama pull {target_model}" if not model_found else None,
                "message": "Ollama is running and ready." if model_found else f"Model '{target_model}' not found. Run 'ollama pull {target_model}'."
            }
        else:
            return {
                "running": False,
                "model_available": False,
                "target_model": target_model,
                "available_models": [],
                "pull_command": f"ollama pull {target_model}",
                "message": f"Ollama returned status code {response.status_code}."
            }
    except requests.exceptions.ConnectionError:
        return {
            "running": False,
            "model_available": False,
            "target_model": target_model,
            "available_models": [],
            "pull_command": f"ollama pull {target_model}",
            "message": "Ollama is not running. Please start Ollama using 'ollama serve' and try again."
        }
    except Exception as e:
        return {
            "running": False,
            "model_available": False,
            "target_model": target_model,
            "available_models": [],
            "pull_command": f"ollama pull {target_model}",
            "message": f"Error connecting to Ollama: {str(e)}"
        }


def generate_legal_prompt(document_text: str) -> str:
    """
    Constructs the prompt adhering strictly to the lab experiment specifications.
    """
    prompt = f"""SYSTEM ROLE:
You are a legal document analysis assistant.

TASK:
Analyze and summarize the provided legal document.

Extract ONLY information that is explicitly present in the document.

Identify:
- Document Type
- Parties
- Purpose
- Obligations
- Rights
- Payment Terms
- Duration
- Termination Conditions
- Confidentiality Requirements
- Important Dates
- Governing Law
- Key Clauses
- Potentially Important Clauses
- Summary

IMPORTANT CONSTRAINT:
Use only information present in the document.
Do not invent facts.
If information is not available, write "Not specified in the document."

OUTPUT:
Return the analysis in a structured JSON format.

Example:
{{
  "document_type": "string",
  "parties": ["string"],
  "purpose": "string",
  "obligations": ["string"],
  "rights": ["string"],
  "payment_terms": "string",
  "duration": "string",
  "termination": "string",
  "confidentiality": "string",
  "important_dates": ["string"],
  "governing_law": "string",
  "key_clauses": ["string"],
  "potentially_important_clauses": ["string"],
  "summary": "string"
}}

LEGAL DOCUMENT TEXT:
\"\"\"
{document_text}
\"\"\"

Provide ONLY valid JSON as your response."""
    return prompt


def clean_and_normalize_json(raw_text: str) -> Dict[str, Any]:
    """
    Cleans raw response from LLM and ensures all expected fields are present.
    """
    text = raw_text.strip()
    
    # Remove markdown code fences if model enclosed JSON in ```json ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # Try finding the first '{' and last '}' in case of leading/trailing commentary
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1 and end_idx != -1:
        text = text[start_idx : end_idx + 1]

    try:
        data = json.loads(text)
    except Exception as e:
        # If standard json load fails, try fixing common trailing comma issue
        fixed_text = re.sub(r",\s*([\]}])", r"\1", text)
        data = json.loads(fixed_text)

    # Normalize fields to guarantee consistency with frontend
    normalized = {}
    list_fields = {
        "parties", "obligations", "rights", 
        "important_dates", "key_clauses", "potentially_important_clauses"
    }
    string_fields = {
        "document_type", "purpose", "payment_terms", 
        "duration", "termination", "confidentiality", 
        "governing_law", "summary"
    }

    for key in DEFAULT_SCHEMA_KEYS:
        val = data.get(key)
        if key in list_fields:
            if isinstance(val, list):
                # Filter empty strings or placeholders
                cleaned_list = [str(item).strip() for item in val if str(item).strip()]
                normalized[key] = cleaned_list if cleaned_list else ["Not specified in the document."]
            elif isinstance(val, str) and val.strip():
                normalized[key] = [val.strip()]
            else:
                normalized[key] = ["Not specified in the document."]
        elif key in string_fields:
            if isinstance(val, str) and val.strip():
                normalized[key] = val.strip()
            elif isinstance(val, list) and len(val) > 0:
                normalized[key] = ", ".join(str(item) for item in val)
            else:
                normalized[key] = "Not specified in the document."
        else:
            normalized[key] = val

    return normalized


def query_ollama_analyze(document_text: str, model_name: str = DEFAULT_MODEL) -> Tuple[bool, Dict[str, Any], str]:
    """
    Calls the local Ollama /api/generate endpoint with stream=False and format=json.
    Returns: (success: bool, data_or_empty: dict, error_message: str)
    """
    status = check_ollama_status(model_name)
    if not status["running"]:
        return False, {}, "Ollama is not running. Please start Ollama using 'ollama serve' and try again."
    
    # Use the detected model or requested model
    active_model = status["actual_model"] if status["actual_model"] else model_name

    prompt = generate_legal_prompt(document_text)

    payload = {
        "model": active_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,  # Low temperature for deterministic legal extraction
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120  # Allow up to 2 minutes for local LLM inference
        )
        
        if response.status_code != 200:
            return False, {}, f"Ollama API returned error HTTP {response.status_code}: {response.text}"

        res_data = response.json()
        raw_response = res_data.get("response", "")
        
        if not raw_response:
            return False, {}, "Ollama returned an empty response."

        analysis_json = clean_and_normalize_json(raw_response)
        return True, analysis_json, ""

    except requests.exceptions.Timeout:
        return False, {}, "Ollama request timed out. The local model took too long to respond."
    except requests.exceptions.ConnectionError:
        return False, {}, "Lost connection to Ollama. Please ensure Ollama is running."
    except json.JSONDecodeError as json_err:
        return False, {}, f"Failed to parse model output as JSON: {str(json_err)}"
    except Exception as e:
        return False, {}, f"Unexpected error during analysis: {str(e)}"
