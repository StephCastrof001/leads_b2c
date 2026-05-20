from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json

app = FastAPI()

# Mock LLM responses for testing
MOCK_BRIEF_RESPONSE = {
    "brief": "Brief creativo para Klipso: Enfocado en la industria SaaS. Con la visión clara de democratizar el diseño digital...",
    "name_suggestions": [
        {
            "name": "Klipso Forge",
            "rationale": "Combina la solidez del sector con la forja del branding interactivo."
        },
        {
            "name": "NovaBrand",
            "rationale": "Representa el renacimiento estético y el brillo de la nueva identidad visual."
        },
        {
            "name": "KlipsoNext",
            "rationale": "Evoca el salto hacia adelante en diseño inteligente y automatización premium."
        }
    ],
    "brandkit_inputs": {
        "brand_name": "Klipso",
        "brand_description": "Pioneering company in SaaS focused on high-end design solutions.",
        "brand_industry": "SaaS",
        "company_keywords": ["moderno", "limpio", "minimalista", "digital", "SaaS"],
        "brand_personality": "Sophistication",
        "target_segment": "startups y creadores de contenido"
    }
}

MOCK_GENERATE_RESPONSE = {
    "palettes": [
        {
            "hex": "#0F172A",
            "name": "Primary Accent",
            "desc": "Reflects the core values, authority, and emotional stability of the brand."
        },
        {
            "hex": "#0EA5E9",
            "name": "Secondary Accent",
            "desc": "Brings balance, representing growth, modern technology, and clarity."
        },
        {
            "hex": "#F8FAFC",
            "name": "Active Highlight",
            "desc": "A vibrant touchpoint designed to guide user attention and highlight interactive elements."
        }
    ],
    "typography": [
        {
            "type": "Heading Font",
            "name": "Montserrat",
            "desc": "Used for hero titles and major visual typography to establish brand presence."
        },
        {
            "type": "Body Font",
            "name": "Inter",
            "desc": "Used for reading legibility across standard content and descriptions."
        },
        {
            "type": "Accent Font",
            "name": "Fira Code",
            "desc": "Used for labels, code segments, secondary CTAs, or highlighted captions."
        }
    ],
    "taglines": {
        "en": "Simplifying the future.",
        "es": "Simplificando el futuro."
    },
    "logos": [
        "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
    ]
}


class BriefRequest(BaseModel):
    company_name: str
    vision: str
    mission: str
    purpose: str
    values: List[str]
    industry: str
    keywords: str
    target_audience: str


class GenerateRequest(BaseModel):
    brandkit_inputs: Dict[str, Any]
    direction: str


def query_gemini(prompt: str) -> Dict[str, Any]:
    """Mock function to simulate Gemini API call"""
    return MOCK_BRIEF_RESPONSE


def query_together_ai(prompt: str) -> Dict[str, Any]:
    """Mock function to simulate Together AI API call"""
    return MOCK_GENERATE_RESPONSE


@app.post("/brief")
async def create_brief(request: BriefRequest):
    """Generates a refined creative brief, name suggestions, and structured inputs for the brand generator."""
    try:
        result = query_gemini(json.dumps({
            "company_name": request.company_name,
            "vision": request.vision,
            "mission": request.mission,
            "purpose": request.purpose,
            "values": request.values,
            "industry": request.industry,
            "keywords": request.keywords,
            "target_audience": request.target_audience
        }))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def generate_brandkit(request: GenerateRequest):
    """Generates a comprehensive brand identity kit including custom color rationales, typography, slogans, and logos."""
    try:
        result = query_together_ai(json.dumps({
            "brandkit_inputs": request.brandkit_inputs,
            "direction": request.direction
        }))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
