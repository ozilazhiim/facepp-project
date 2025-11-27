# Gunakan image Python yang ringan
FROM python:3.9-slim

# Set folder kerja di dalam container
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy sisa kode (app.py)
COPY . .

# Expose port default Streamlit
EXPOSE 8501

# Perintah kesehatan (Healthcheck)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Jalankan aplikasi saat container start
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]