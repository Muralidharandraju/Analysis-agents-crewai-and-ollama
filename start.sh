#!/bin/bash
set -e

# Start Ollama server in the background
ollama serve &

# Wait for Ollama server to be ready
until curl -s http://localhost:11434/api/tags > /dev/null; do
  echo "Waiting for Ollama server..."
  sleep 2
done

# Pull the Gemma3 model
ollama pull gemma3

# Start the FastAPI app in the background
uvicorn app:app --host 0.0.0.0 --port 8090 &
FASTAPI_PID=$!

# Start the Streamlit app in the background
streamlit run /streamlit_app.py --server.port 8000 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# Wait for both to exit
wait $FASTAPI_PID $STREAMLIT_PID
