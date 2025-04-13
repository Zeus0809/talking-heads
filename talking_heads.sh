#!/bin/bash

tmux new-session -d -s talking-heads-ai '/Users/illiakozlov/TalkingHeadsAI/venv/bin/streamlit run /Users/illiakozlov/TalkingHeadsAI/app.py'

tmux new-session -d -s tunnel 'cloudflared tunnel --url http://localhost:8501'

echo "Streamlit and Cloudflare tunnel started in tmux sessions: 'streamlit' and 'tunnel'"

