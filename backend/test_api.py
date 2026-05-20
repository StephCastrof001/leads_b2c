from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# TEST 1 — /brief devuelve campo 'brief'
def test_brief_returns_brief_field():
    """Test that /brief returns the 'brief' field in response."""
    request_data = {
        "company_name": "Klipso",
        "vision": "democratizar el diseño digital",
        "mission": "branding premium accesible",
        "purpose": "Hacer diseño instantáneo de calidad profesional para todos",
        "values": ["innovacion", "agilidad", "sencillez"],
        "industry": "SaaS",
        "keywords": "moderno, limpio, minimalista, digital",
        "target_audience": "startups y creadores de contenido"
    }
    
    response = client.post("/brief", json=request_data)
    
    assert response.status_code == 200
    assert 'brief' in response.json()


# TEST 2 — /brief devuelve campo 'name_suggestions' como lista de 3
def test_brief_returns_name_suggestions_list_of_3():
    """Test that /brief returns 'name_suggestions' as a list of 3 items."""
    request_data = {
        "company_name": "Klipso",
        "vision": "democratizar el diseño digital",
        "mission": "branding premium accesible",
        "purpose": "Hacer diseño instantáneo de calidad profesional para todos",
        "values": ["innovacion", "agilidad", "sencillez"],
        "industry": "SaaS",
        "keywords": "moderno, limpio, minimalista, digital",
        "target_audience": "startups y creadores de contenido"
    }
    
    response = client.post("/brief", json=request_data)
    
    assert response.status_code == 200
    assert 'name_suggestions' in response.json()
    assert len(response.json()['name_suggestions']) == 3


# TEST 3 — /brief devuelve campo 'logo_prompt' como string no vacío
def test_brief_returns_logo_prompt_string():
    """Test that /brief returns 'logo_prompt' as a non-empty string."""
    request_data = {
        "company_name": "Klipso",
        "vision": "democratizar el diseño digital",
        "mission": "branding premium accesible",
        "purpose": "Hacer diseño instantáneo de calidad profesional para todos",
        "values": ["innovacion", "agilidad", "sencillez"],
        "industry": "SaaS",
        "keywords": "moderno, limpio, minimalista, digital",
        "target_audience": "startups y creadores de contenido"
    }
    
    response = client.post("/brief", json=request_data)
    
    assert response.status_code == 200
    assert 'logo_prompt' in response.json()
    assert isinstance(response.json()['logo_prompt'], str)
    assert len(response.json()['logo_prompt']) > 20


# TEST 4 — /generate acepta campo 'direction' y devuelve palettes
def test_generate_accepts_direction_and_returns_palettes():
    """Test that /generate accepts 'direction' field and returns 'palettes'."""
    request_data = {
        "brandkit_inputs": {
            "brand_name": "Klipso",
            "brand_description": "Pioneering company in SaaS focused on high-end design solutions.",
            "brand_industry": "SaaS",
            "company_keywords": ["moderno", "limpio", "minimalista", "digital", "SaaS"],
            "brand_personality": "Sophistication",
            "target_segment": "startups y creadores de contenido"
        },
        "direction": "Minimal"
    }
    
    response = client.post("/generate", json=request_data)
    
    assert response.status_code == 200
    assert 'palettes' in response.json()


# TEST 5 — /generate devuelve taglines con campos 'en' y 'es'
def test_generate_returns_taglines_with_en_and_es():
    """Test that /generate returns 'taglines' with 'en' and 'es' fields."""
    request_data = {
        "brandkit_inputs": {
            "brand_name": "Klipso",
            "brand_description": "Pioneering company in SaaS focused on high-end design solutions.",
            "brand_industry": "SaaS",
            "company_keywords": ["moderno", "limpio", "minimalista", "digital", "SaaS"],
            "brand_personality": "Sophistication",
            "target_segment": "startups y creadores de contenido"
        },
        "direction": "Minimal"
    }
    
    response = client.post("/generate", json=request_data)
    
    assert response.status_code == 200
    assert 'taglines' in response.json()
    assert 'en' in response.json()['taglines']
    assert 'es' in response.json()['taglines']
