import os
import requests
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:3001/api/v1"
API_KEY = os.getenv("ANYTHINGLLM_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# CSV paths
HEALTHCARE_CSV = Path("data/salud/healthcare_faq.csv")
ECOMMERCE_CSV = Path("data/ecommerce/ecommerce_faq.csv")

# Workspace names
WORKSPACE_NAMES = ["klipso-salud", "klipso-ecommerce"]

# System prompt (bilingual)
SYSTEM_PROMPT = """Responde en el idioma en que te escriban. Si espanol responde en espanol. If English respond in English."""

def get_existing_workspace_id(name: str) -> str:
    """Get workspace ID from existing klipso-banca workspace"""
    response = requests.get(f"{API_BASE_URL}/workspaces", headers=HEADERS)
    if response.status_code == 200:
        workspaces = response.json()
        for ws in workspaces:
            if ws.get("name") == "klipso-banca":
                return ws.get("embedId")
    return None

def create_workspace(name: str, embed_id: str) -> dict:
    """Create a new workspace via API"""
    payload = {
        "name": name,
        "embedId": embed_id,
        "systemPrompt": SYSTEM_PROMPT
    }
    response = requests.post(f"{API_BASE_URL}/workspaces", headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to create workspace {name}: {response.text}")

def upload_csv_to_workspace(embed_id: str, csv_path: Path) -> bool:
    """Upload CSV file to workspace"""
    if not csv_path.exists():
        print(f"Warning: CSV file not found: {csv_path}")
        return False
    
    with open(csv_path, "rb") as f:
        files = {"file": (csv_path.name, f)}
        response = requests.post(f"{API_BASE_URL}/workspaces/{embed_id}/documents", headers=HEADERS, files=files)
        return response.status_code == 200

def save_workspace_ids(workspaces: list, output_path: Path):
    """Save workspace IDs to markdown file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write("# Workspace IDs\n\n")
        for ws in workspaces:
            f.write(f"## {ws['name']}\n\n")
            f.write(f"- **Slug**: {ws.get('slug', 'N/A')}\n")
            f.write(f"- **Embed ID**: {ws.get('embedId', 'N/A')}\n\n")

def main():
    print("Creating multisector workspaces...")
    
    # Get existing workspace ID from klipso-banca
    existing_embed_id = get_existing_workspace_id("klipso-banca")
    if not existing_embed_id:
        print("Warning: Could not find klipso-banca workspace. Using default embedId.")
        existing_embed_id = "klipso-banca"
    
    created_workspaces = []
    
    for name in WORKSPACE_NAMES:
        print(f"\nCreating workspace: {name}")
        
        # Create workspace
        workspace = create_workspace(name, existing_embed_id)
        created_workspaces.append(workspace)
        print(f"✓ Created: {name} (Embed ID: {workspace.get('embedId')})")
        
        # Upload CSV
        csv_path = HEALTHCARE_CSV if "salud" in name else ECOMMERCE_CSV
        if upload_csv_to_workspace(workspace.get("embedId"), csv_path):
            print(f"✓ Uploaded CSV for {name}")
        else:
            print(f"⚠ CSV upload for {name} may have failed")
    
    # Save workspace IDs
    save_workspace_ids(created_workspaces, Path("docs/workspace_ids.md"))
    print("\n✓ Saved workspace IDs to docs/workspace_ids.md")
    
    # Verify workspaces
    print("\nVerifying workspaces...")
    response = requests.get(f"{API_BASE_URL}/workspaces", headers=HEADERS)
    all_workspaces = response.json()
    
    print(f"\nTotal workspaces: {len(all_workspaces)}")
    for ws in all_workspaces:
        print(f"  - {ws.get('name')}")
    
    expected_count = 3  # klipso-banca + klipso-salud + klipso-ecommerce
    if len(all_workspaces) == expected_count:
        print(f"\n✓ SUCCESS: Found {expected_count} workspaces as expected")
    else:
        print(f"\n⚠ WARNING: Expected {expected_count} workspaces, found {len(all_workspaces)}")

if __name__ == "__main__":
    main()
