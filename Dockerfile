FROM python:3.12

# Install dependencies for Ollama
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh


# Copy application code
COPY . .

# Copy the startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the FastAPI port
EXPOSE 8000 
# Set the entry point to the startup script
ENTRYPOINT ["/start.sh"]

CMD ["python", "app.py"]