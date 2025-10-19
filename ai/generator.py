# ai/generator.py
"""
Handles prompt construction and LLM-based generation for the RAG pipeline.
"""

import os
from typing import Dict, Any, List
from textwrap import dedent
from dotenv import load_dotenv
import requests
import json

load_dotenv()


def make_prompt(query: str, context: dict) -> str:
    """
    Construct a text prompt combining user query and retrieved context.
    """
    case_summaries = "\n\n".join(
        f"• {hit.get('text', '')[:80]}\n{hit.get('text', '')[:300]}..." 
        for hit in context.get("cases", [])
    )
    kb_summaries = "\n\n".join(
        f"• {hit.get('text', '')[:80]}\n{hit.get('text', '')[:300]}..." 
        for hit in context.get("knowledge", [])
    )

    prompt = dedent(
        f"""
        You are a reliability assistant. Answer the user query based on the retrieved context.

        === CASE LOGS ===
        {case_summaries or 'No similar cases found.'}

        === KNOWLEDGE BASE ===
        {kb_summaries or 'No KB matches found.'}

        === QUERY ===
        {query}

        Provide a concise, clear answer referencing the above context.
        """
    ).strip()

    return prompt


def generate_answer(prompt: str) -> str:
    """
    Generate a response using a local or remote LLM.
    Priority:
      1. OpenAI API (OPENAI_API_KEY)
      2. Ollama local model (if installed)
    """
    import subprocess

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing API key environment variable")
    url = "https://psacodesprint2025.azure-api.net/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2025-01-01-preview"

    headers = {
        "Content-Type":"application/json",
        "api-key":api_key,
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        raise Exception(f"API call failed: {response.status_code}, {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]

    # if os.getenv("OPENAI_API_KEY"):
    #     from openai import OpenAI

    #     client = OpenAI()
    #     completion = client.chat.completions.create(
    #         model="gpt-4o-mini",
    #         messages=[{"role": "user", "content": prompt}],
    #     )
    #     return completion.choices[0].message.content

    # # fallback: try local Ollama if available
    # try:
    #     result = subprocess.run(
    #         ["ollama", "run", "llama3.1", prompt],
    #         capture_output=True,
    #         text=True,
    #         timeout=60,
    #     )
    #     return result.stdout.strip() or "(No output from Ollama)"
    # except Exception as e:
    #     return f"LLM provider not configured: {e}"
