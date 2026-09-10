"""
backend/server.py
-----------------
FastAPI backend that proxies chat requests to IBM watsonx.ai and also
exposes the raw nutrition tools as REST endpoints.

Run with:
    pip install fastapi uvicorn httpx python-dotenv
    uvicorn backend.server:app --reload --port 8000

Environment (set in .env or as env-vars):
    WX_API_KEY      = 7ffd4adb-1ca1-44f8-b51a-07d094134d43
    WX_PROJECT_ID   = 7941a5f5-93ea-4733-b512-8683d256b20e
    WX_MODEL_ID     = meta-llama/llama-3-3-70b-instruct
    WX_URL          = https://au-syd.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env from the same directory as this file, regardless of where uvicorn is run from
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
WX_API_KEY    = os.getenv("WX_API_KEY")
WX_PROJECT_ID = os.getenv("WX_PROJECT_ID")
WX_MODEL_ID   = os.getenv("WX_MODEL_ID",  "mistralai/mistral-small-3-1-24b-instruct-2503")
WX_CHAT_URL   = os.getenv("WX_URL",       "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29")
WX_TOKEN_URL  = "https://iam.cloud.ibm.com/identity/token"

SYSTEM_PROMPT = """You are an expert Nutrition Agent with deep knowledge of food science,
dietetics, and personalised health planning. You help users:

1. Understand the nutritional content of any food item — macros (calories, protein,
   carbohydrates, fat) and micros (vitamins, minerals).
2. Create personalised diet plans based on their health goals, body metrics, and
   dietary restrictions.
3. Answer general questions about healthy eating, hydration, meal timing, and lifestyle.

Guidelines:
- Be warm, encouraging, and non-judgmental.
- Present nutrient data in a clear, formatted way using markdown lists or tables.
- For diet plans, always collect: goal, age, gender, weight (kg), height (cm),
  activity level, and any dietary restrictions before generating the plan.
- Always remind users with medical conditions to consult a registered dietitian or doctor.
- Never recommend dangerous practices (extreme restriction, unsafe supplements, etc.)."""

app = FastAPI(title="Nutrition Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# IAM token helper
# ---------------------------------------------------------------------------
_token_cache: dict = {}


async def get_iam_token() -> str:
    """Exchange API key for a short-lived IAM bearer token."""
    import time
    now = time.time()
    if _token_cache.get("token") and _token_cache.get("expires", 0) > now + 60:
        return _token_cache["token"]

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            WX_TOKEN_URL,
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": WX_API_KEY,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code != 200:
            raise HTTPException(502, f"IAM token error: {resp.text}")
        data = resp.json()
        _token_cache["token"] = data["access_token"]
        _token_cache["expires"] = now + data.get("expires_in", 3600)
        return _token_cache["token"]


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    max_tokens: Optional[int] = Field(default=2048)
    temperature: Optional[float] = Field(default=0.7)


class ChatResponse(BaseModel):
    reply: str
    model: str
    usage: dict


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "model": WX_MODEL_ID}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a multi-turn conversation to watsonx.ai and return the assistant reply.
    """
    token = await get_iam_token()

    # Build the messages payload
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in request.messages:
        messages.append({"role": m.role, "content": m.content})

    payload = {
        "model_id": WX_MODEL_ID,
        "project_id": WX_PROJECT_ID,
        "messages": messages,
        "parameters": {
            "max_new_tokens": request.max_tokens,
            "temperature": request.temperature,
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            WX_CHAT_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code != 200:
        raise HTTPException(resp.status_code, f"watsonx error: {resp.text}")

    data = resp.json()
    try:
        reply = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
    except (KeyError, IndexError) as exc:
        raise HTTPException(500, f"Unexpected response format: {exc}\n{data}")

    return ChatResponse(reply=reply, model=WX_MODEL_ID, usage=usage)


@app.get("/nutrients/{food_item}")
async def get_nutrients(food_item: str, serving_size_grams: float = 100.0):
    """
    Quick nutrient lookup — calls the watsonx model with a structured prompt.
    """
    token = await get_iam_token()

    prompt_text = (
        f"Give me detailed nutritional information for {food_item} "
        f"per {serving_size_grams}g serving. Include calories, protein, "
        f"carbohydrates, fat, key vitamins and minerals, health benefits, "
        f"and any dietary cautions. Format clearly with markdown."
    )

    payload = {
        "model_id": WX_MODEL_ID,
        "project_id": WX_PROJECT_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text},
        ],
        "parameters": {"max_new_tokens": 1024, "temperature": 0.3},
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            WX_CHAT_URL,
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )

    if resp.status_code != 200:
        raise HTTPException(resp.status_code, resp.text)

    data = resp.json()
    reply = data["choices"][0]["message"]["content"]
    return {"food_item": food_item, "serving_size_grams": serving_size_grams, "info": reply}
