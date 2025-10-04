FROM apache/airflow:2.5.1

# Install Postgres provider, psycopg2, HuggingFace SDK
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt