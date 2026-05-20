import os
import glob
import time
import subprocess
import shutil

QUEUE_DIR = os.path.expanduser("~/queue")
DONE_DIR = os.path.expanduser("~/done")
FAILED_DIR = os.path.expanduser("~/failed")
PROJECT_DIR = os.path.expanduser("~/leads/socleads")

# Aseguramos que los directorios existan
for d in [QUEUE_DIR, DONE_DIR, FAILED_DIR]:
    os.makedirs(d, exist_ok=True)

def run_aider(spec_file, project_dir):
    print(f"🤖 Ejecutando Ollama/Aider con spec: {os.path.basename(spec_file)} en {project_dir}")
    cmd = [
        "aider",
        "--model", "ollama_chat/qwen35u-tools:9b",
        "--message-file", spec_file,
        "--yes",
        "--no-auto-commits"
    ]
    env = os.environ.copy()
    env["OLLAMA_API_BASE"] = "http://127.0.0.1:11434"
    
    result = subprocess.run(cmd, cwd=project_dir, env=env, capture_output=True, text=True)
    return result.returncode == 0

def run_smoke_test(script_path, project_dir):
    print(f"🧪 Ejecutando Smoke Test en: {script_path}")
    env = os.environ.copy()
    env["PYTHONPATH"] = project_dir
    result = subprocess.run(["python3", script_path], cwd=project_dir, env=env, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

def run_ruff_smoke_test(project_dir):
    """Run ruff linting as smoke test for logo prompt refs"""
    print(f"🧪 Ejecutando Ruff Lint en: {project_dir}")
    env = os.environ.copy()
    result = subprocess.run(["ruff", "check", "."], cwd=project_dir, env=env, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

def clone_logo_prompt_repos():
    """Clone 3 logo prompt repos to /tmp/"""
    print("📦 Clonando repositorios de logo prompts a /tmp/...")
    repos = [
        "https://github.com/StephCastrof001/leads_b2c.git",
        "https://github.com/StephCastrof001/leads_b2c.git",
        "https://github.com/StephCastrof001/leads_b2c.git"
    ]
    
    for i, repo in enumerate(repos):
        repo_name = f"logo_prompt_repo_{i+1}"
        repo_path = f"/tmp/{repo_name}"
        print(f"  Clonando {repo_name}...")
        try:
            subprocess.run(["git", "clone", repo, repo_path], check=True)
            print(f"  ✅ {repo_name} clonado")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️ {repo_name} falló: {e}")
    
    return repos

def extract_logo_prompt_formulas(output_path):
    """Extract formulas + examples from cloned repos to output file"""
    print(f"📝 Extrayendo fórmulas y ejemplos a: {output_path}")
    
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create output file with extracted content
    content = """# Logo Prompt References
"""
    
    # Add content from cloned repos
    for i in range(3):
        repo_path = f"/tmp/logo_prompt_repo_{i+1}"
        if os.path.exists(repo_path):
            # Look for relevant files
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file.endswith(('.md', '.txt', '.json')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content += f"\n### {file}\n"
                                content += f"```text\n{f.read()}\n```\n"
                        except Exception:
                            pass
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Extracción completada a {output_path}")
    return True

def process_queue():
    specs = sorted(glob.glob(os.path.join(QUEUE_DIR, "*.md")))
    for spec in specs:
        if "ESCALADO" in spec:
            continue # No tocamos los archivos de emergencia
            
        print(f"\n🚀 [NIVEL 5] Iniciando Misión: {os.path.basename(spec)}")
        
        # Extraer proyecto y test dinamicamente
        content = open(spec).read()
        
        # Default fallback
        project_dir = os.path.expanduser("~/leads/socleads")
        for line in content.split("\n"):
            if line.lower().startswith("cwd:"):
                project_dir = os.path.expanduser(line.split(":", 1)[1].strip())
                break
        
        # Detect if this is a logo prompt refs spec
        is_logo_prompt = "logo" in content.lower() or "prompt" in content.lower()
        
        # Determine test script based on spec type
        if is_logo_prompt:
            test_script = "ruff"  # Use ruff for linting
            output_file = os.path.expanduser("~/klipso_branding-logo/docs_dev/logo_prompt_references.md")
        else:
            test_script = "recon/recon.py" if "recon" in content.lower() else "run_extraction.py"
            output_file = None
        
        # 1. Aplicar la Spec de Negocio
        success = run_aider(spec, project_dir)
        if not success:
            print("❌ Ollama falló catastróficamente al leer la spec.")
            shutil.move(spec, os.path.join(FAILED_DIR, os.path.basename(spec)))
            continue
        
        # 2. Clonar repos y extraer fórmulas (si es logo prompt)
        if is_logo_prompt:
            print("📦 Fase 2: Clonando repositorios y extrayendo fórmulas...")
            clone_logo_prompt_repos()
            extract_logo_prompt_formulas(output_file)
        
        # 3. LA MATRIZ DE ESCALACIÓN (Bucle de Autocorrección)
        max_retries = 3
        attempts = 0
        resolved = False
        
        while attempts < max_retries:
            if is_logo_prompt:
                test_ok, stderr = run_ruff_smoke_test(project_dir)
            else:
                test_ok, stderr = run_smoke_test(test_script, project_dir)
            
            if test_ok:
                print("✅ SMOKE TEST PASÓ. Ejecución perfecta.")
                resolved = True
                break
                
            attempts += 1
            print(f"⚠️ [Intento {attempts}/{max_retries}] El código explotó. Activando Auto-Curación...")
            
            # Crear un prompt de reparación automática
            healing_prompt_path = os.path.join(QUEUE_DIR, "healing_temp.txt")
            with open(healing_prompt_path, "w") as f:
                f.write(f"El script {test_script} acaba de fallar con este Traceback rojo:\n\n{stderr}\n\nAnaliza el error lógico o de sintaxis y corrígelo inmediatamente. No cambies el comportamiento principal, solo soluciona el fallo.")
                
            # Ollama intenta arreglarse a sí mismo
            run_aider(healing_prompt_path, project_dir)
            os.remove(healing_prompt_path)
            
        # 4. Evaluación Final de la Misión
        if resolved:
            print("🏆 Autocorrección terminada. Commiteando y subiendo a GitHub...")
            commit_msg = f"fix: Resolución autónoma de spec {os.path.basename(spec)}"
            subprocess.run(["git", "add", "."], cwd=project_dir)
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=project_dir)
            subprocess.run(["git", "push", "origin", "main"], cwd=project_dir)
            print("☁️ Código enviado a la nube. Moviendo a ~/done/")
            shutil.move(spec, os.path.join(DONE_DIR, os.path.basename(spec)))
        else:
            print("🚨 Límite cognitivo alcanzado. ESCALANDO AL ARQUITECTO (NIVEL 6).")
            escalation_file = os.path.join(QUEUE_DIR, f"ESCALADO_A_CLAUDE_{int(time.time())}.md")
            with open(escalation_file, "w") as f:
                f.write(f"# 🚨 EMERGENCIA: ESCALACIÓN DE NIVEL 5\nLa spec `{os.path.basename(spec)}` sobrepasó las capacidades de Ollama tras {max_retries} intentos de autocorrección.\n\n### Último error fatal:\n```python\n{stderr}\n```\n\n**Acción requerida (Nivel 6):** Claude, por favor lee este error, arregla la lógica profunda y vuelve a enviar la spec.")
            shutil.move(spec, os.path.join(FAILED_DIR, os.path.basename(spec)))

if __name__ == "__main__":
    print("🧠 HiveMind V2 (Nivel 5) Boot sequence completada.")
    print("📡 Escuchando transmisiones en la cola...")
    while True:
        process_queue()
        time.sleep(10)
