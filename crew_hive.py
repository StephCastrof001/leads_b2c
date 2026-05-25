import os
import glob
from pathlib import Path

# Queue directory configuration
QUEUE_DIR = os.path.expanduser("~/queue")

def _ensure_repo_in_md(task_path: str) -> None:
    p = Path(task_path)
    content = p.read_text()
    if "REPO:" not in content:
        proj_name = p.parent.name
        if proj_name != "queue":
            p.write_text(f"REPO: ~/{proj_name}\n" + content)

def process_unit(spec: str) -> None:
    """Process a single task specification file."""
    print(f"Processing: {spec}")
    # Implementation would go here
    pass

def process_queue():
    subdir_specs = sorted(glob.glob(os.path.join(QUEUE_DIR, "*", "*.md")))
    root_specs = sorted(glob.glob(os.path.join(QUEUE_DIR, "*.md")))
    specs = subdir_specs + root_specs
    if not specs:
        print(" Cola vacía. Sin misiones pendientes.")
        return
    for spec in specs:
        if "ESCALADO" in spec:
            continue
        _ensure_repo_in_md(spec)
        process_unit(spec)

def main():
    process_queue()

if __name__ == "__main__":
    main()
