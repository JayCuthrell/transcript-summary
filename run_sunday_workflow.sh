#!/usr/bin/env zsh

REPO_DIR="$HOME/github/transcript-summary"
LOG_FILE="$REPO_DIR/sunday_workflow.log"

echo "=== Sunday Podcast Prep Workflow Started: $(date) ===" >> "$LOG_FILE"
cd "$REPO_DIR" || { echo "Directory $REPO_DIR not found!" >> "$LOG_FILE"; exit 1; }

# Rebuild the environment from scratch, just like your manual workflow
echo "Rebuilding virtual environment..." >> "$LOG_FILE"
source ./setup.sh >> "$LOG_FILE" 2>&1

# Execute scripts
echo "Executing pull-transcripts.py..." >> "$LOG_FILE"
python3 -u pull-transcripts.py >> "$LOG_FILE" 2>&1

echo "Executing process_techmeme.py..." >> "$LOG_FILE"
python3 -u process_techmeme.py >> "$LOG_FILE" 2>&1

echo "=== Sunday Podcast Prep Workflow Finished: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"