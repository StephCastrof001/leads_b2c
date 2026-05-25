#!/bin/bash

# Queue Watcher V2 - Detects files in ~/queue/ subdirectories with inotifywait recursively

QUEUE_DIR="$HOME/queue"

# Ensure queue directory exists
mkdir -p "$QUEUE_DIR"

# Function to recursively watch queue directory
watch_queue_recursive() {
    echo "👁️  Watching $QUEUE_DIR recursively for new files..."
    
    # Use inotifywait to watch for file creation events recursively
    inotifywait -m -r -e close_write -e moved_to --format '%w%f' "$QUEUE_DIR" 2>/dev/null | while read -r file; do
        echo "📥 New file detected: $file"
        
        # Get the relative path from queue directory
        rel_path="${file#$HOME/queue/}"
        
        # Check if it's a markdown spec file
        if [[ "$file" == *.md ]]; then
            echo "🚀 Processing spec file: $rel_path"
            
            # Move to done directory after processing
            sleep 2
            
            # Signal the orchestrator to process
            echo "NEW_SPEC:$rel_path" >> "$HOME/queue/.processing"
        fi
    done
}

# Function to check for new specs periodically (fallback)
check_queue_periodically() {
    echo "🔍 Checking queue directory for new files..."
    
    # Find all markdown files recursively
    while IFS= read -r -d '' file; do
        if [[ "$file" == *.md ]]; then
            echo "📥 Found new spec: $file"
            
            # Get relative path
            rel_path="${file#$HOME/queue/}"
            
            # Check if already being processed
            if [[ ! -f "$HOME/queue/.processing" ]] || ! grep -q "NEW_SPEC:$rel_path" "$HOME/queue/.processing" 2>/dev/null; then
                echo "🚀 Starting processing: $rel_path"
                
                # Move to done directory after processing
                sleep 2
                
                # Signal the orchestrator to process
                echo "NEW_SPEC:$rel_path" >> "$HOME/queue/.processing"
            fi
        fi
    done < <(find "$QUEUE_DIR" -type f -name "*.md" -print0 2>/dev/null)
}

# Main execution
echo "🧠 HiveMind V2 (Nivel 5) Boot sequence completada."
echo "📡 Escuchando transmisiones en la cola..."

# Use inotifywait for real-time monitoring
if command -v inotifywait &> /dev/null; then
    watch_queue_recursive
else
    echo "⚠️  inotifywait not found, falling back to periodic check..."
    check_queue_periodically
fi
