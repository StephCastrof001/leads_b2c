#!/bin/bash

# Configuration
QUEUE_DIR="$HOME/queue"
LOG="$HOME/queue-watcher.log"

# Ensure directories exist
mkdir -p "$QUEUE_DIR"

# Start watching for file changes
inotifywait -r -q -e close_write,moved_to --include '.*\.(md|json)$' "$QUEUE_DIR" >> "$LOG" 2>&1

# Get the first spec file (now looking in subdirs too)
SPEC=$(ls "$QUEUE_DIR"/*/*.md "$QUEUE_DIR"/*/*.json 2>/dev/null | head -1)

if [ -n "$SPEC" ]; then
    echo "Found spec file: $SPEC"
    # Process the spec file...
fi

# Keep the script running
wait
