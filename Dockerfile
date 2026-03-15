# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose Streamlit port
EXPOSE 8080

# Run Streamlit
CMD streamlit run app/main.py --server.port 8080 --server.address 0.0.0.0 --browser.serverAddress=0.0.0.0