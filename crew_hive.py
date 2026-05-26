from pathlib import Path

# ... existing imports and code ...

subdir = Path("queue")

def _ensure_repo_in_md(task_path: Path) -> None:
    content = task_path.read_text()
    if 'REPO:' not in content:
        proj_name = task_path.parent.name
        task_path.write_text(f'REPO: ~/{proj_name}\n' + content)


# ... existing code ...

def process_queue():
    # ... existing code ...
    
    # Find each .md in subdir
    for task_path in subdir.iterdir():
        if task_path.suffix == '.md':
            # Call _ensure_repo_in_md right after finding each .md before processing
            _ensure_repo_in_md(task_path)
            
            # ... rest of processing code ...
