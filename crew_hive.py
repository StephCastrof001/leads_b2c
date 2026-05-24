#!/usr/bin/env python3
"""
crew_hive.py - Orchestrator for running tasks from .md files in project directories.
"""

import argparse
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List
import re

# Default paths
DEFAULT_QUEUE_DIR = os.path.expanduser("~/queue")
DEFAULT_WORK_DIR = tempfile.mkdtemp(prefix="crew_hive_work_")

class ProjectManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.work_dir = Path(DEFAULT_WORK_DIR) / self.project_path.name
        self.project_name = self.project_path.name
        
    def ensure_project_exists(self) -> bool:
        """Clone or update the project repository."""
        if not self.project_path.exists():
            log(f"Cloning project from {self.project_path}...")
            try:
                subprocess.run(
                    ["git", "clone", str(self.project_path), str(self.work_dir)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                log(f"Project cloned to {self.work_dir}")
                return True
            except subprocess.CalledProcessError as e:
                log(f"Error cloning project: {e.stderr}")
                return False
        else:
            log(f"Project already exists at {self.work_dir}")
            return True
    
    def update_project(self) -> bool:
        """Update the project repository."""
        if self.work_dir.exists():
            try:
                subprocess.run(
                    ["git", "-C", str(self.work_dir), "pull"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                log("Project updated successfully")
                return True
            except subprocess.CalledProcessError as e:
                log(f"Error updating project: {e.stderr}")
                return False
        return False
    
    def get_task_files(self) -> List[Path]:
        """Find all .md task files in the project directory."""
        task_files = []
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.md'):
                    task_files.append(Path(root) / file)
        return task_files

def log(message: str):
    """Print log message with timestamp."""
    timestamp = os.path.basename(os.path.dirname(__file__))
    print(f"[{timestamp}] {message}")

def run_task(task_file: Path, project_manager: ProjectManager) -> bool:
    """Execute a task from a .md file."""
    log(f"Processing task: {task_file}")
    
    # Ensure project exists
    if not project_manager.ensure_project_exists():
        return False
    
    # Read task instructions
    try:
        with open(task_file, 'r') as f:
            task_content = f.read()
        log(f"Task content: {task_content[:200]}...")
    except Exception as e:
        log(f"Error reading task file: {e}")
        return False
    
    # Extract commands/actions from .md file
    # Look for common patterns like:
    # - Commands in code blocks
    # - TODO items
    # - Specific action keywords
    
    commands = []
    
    # Find code blocks with commands
    code_blocks = re.findall(r'```(?:bash|sh|python|py)?\n(.*?)```', task_content, re.DOTALL)
    for block in code_blocks:
        commands.append(block.strip())
    
    # Find TODO items
    todos = re.findall(r'(?:TODO|FIXME):?\s*(.+)', task_content)
    for todo in todos:
        commands.append(f"# TODO: {todo}")
    
    # Execute commands
    for cmd in commands:
        if cmd and not cmd.startswith('#'):
            log(f"Executing: {cmd[:100]}...")
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=str(project_manager.work_dir),
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    log(f"Output: {result.stdout}")
                if result.stderr:
                    log(f"Error: {result.stderr}")
                if result.returncode != 0:
                    log(f"Command failed with code {result.returncode}")
            except Exception as e:
                log(f"Error executing command: {e}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Run tasks from .md files in project directories")
    parser.add_argument(
        "--project", 
        "-p",
        default=os.path.join(DEFAULT_QUEUE_DIR, os.environ.get("PROJECT_NAME", "default")),
        help="Path to the project directory (default: ~/queue/<project_name>/)"
    )
    parser.add_argument(
        "--task", 
        "-t",
        default=None,
        help="Specific task file to run (optional, will scan all .md files if not provided)"
    )
    parser.add_argument(
        "--work-dir",
        "-w",
        default=DEFAULT_WORK_DIR,
        help="Working directory for temporary files"
    )
    
    args = parser.parse_args()
    
    # Create project manager
    project_manager = ProjectManager(args.project)
    
    # Ensure work directory exists
    project_manager.work_dir.mkdir(parents=True, exist_ok=True)
    
    # Get task files
    if args.task:
        task_files = [Path(args.task)]
    else:
        task_files = project_manager.get_task_files()
    
    if not task_files:
        log(f"No task files found in {project_manager.project_path}")
        return 1
    
    log(f"Found {len(task_files)} task file(s)")
    
    # Run each task
    success_count = 0
    for task_file in task_files:
        if run_task(task_file, project_manager):
            success_count += 1
    
    log(f"Completed {success_count}/{len(task_files)} tasks successfully")
    return 0 if success_count == len(task_files) else 1

if __name__ == "__main__":
    sys.exit(main())
