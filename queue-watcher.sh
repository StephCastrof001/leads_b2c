#!/bin/bash

# queue-watcher.sh - Monitors ~/queue/ for new projects and tasks

QUEUE_DIR="$HOME/queue"
LOG_FILE="$HOME/queue/queue-watcher.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if a directory is a valid project
is_valid_project() {
    local dir="$1"
    if [ -d "$dir" ] && [ -n "$(ls -A "$dir" 2>/dev/null)" ]; then
        return 0
    fi
    return 1
}

# Function to find .md task files in a project directory
find_task_files() {
    local project_dir="$1"
    find "$project_dir" -maxdepth 2 -name "*.md" -type f 2>/dev/null
}

# Main loop - Monitor ~/queue/ for new projects
while true; do
    log_message "Scanning $QUEUE_DIR for new projects..."
    
    # Find all subdirectories in ~/queue/
    for project_dir in "$QUEUE_DIR"/*/; do
        # Skip if not a directory
        [ -d "$project_dir" ] || continue
        
        # Remove trailing slash
        project_dir="${project_dir%/}"
        
        # Check if it's a valid project directory
        if is_valid_project "$project_dir"; then
            log_message "Found project directory: $project_dir"
            
            # Find .md task files in this project
            task_files=$(find_task_files "$project_dir")
            
            if [ -n "$task_files" ]; then
                log_message "Found task files in $project_dir:"
                echo "$task_files" | while read -r task_file; do
                    log_message "  - Task: $task_file"
                    # Pass the project directory to crew_hive.py
                    python3 "$HOME/crew_hive.py" --project "$project_dir" --task "$task_file"
                done
            else
                log_message "No task files found in $project_dir"
            fi
        fi
    done
    
    # Wait before next scan
    sleep 30
done
