#!/usr/bin/env zsh

# Define absolute path setup variables - targeting your github directory
REPO_DIR="$HOME/github/transcript-summary"
LOG_FILE="$REPO_DIR/sunday_workflow.log"

echo "=== Sunday Podcast Prep Workflow Started: $(date) ===" >> "$LOG_FILE"

# Navigate to target directory
cd "$REPO_DIR" || { echo "Directory $REPO_DIR not found!" >> "$LOG_FILE"; exit 1; }

# Verify or initialize virtual environment using your matching venv directory configuration
if [ ! -d "my_env" ]; then
    echo "Virtual environment 'my_env' not found. Executing installation setup..." >> "$LOG_FILE"
    # Rely on the environment's zsh path dynamically
    zsh setup.sh >> "$LOG_FILE" 2>&1
fi

# Activate environment cleanly
source my_env/bin/activate >> "$LOG_FILE" 2>&1

# Task 1: Execute existing Premium Podcast analysis pipeline
echo "Executing pull-transcripts.py..." >> "$LOG_FILE"
python3 -u pull-transcripts.py >> "$LOG_FILE" 2>&1

# Task 2: Fetch and process the Techmeme River links
echo "Executing process_techmeme.py..." >> "$LOG_FILE"
python3 -u process_techmeme.py >> "$LOG_FILE" 2>&1

echo "=== Sunday Podcast Prep Workflow Finished: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"