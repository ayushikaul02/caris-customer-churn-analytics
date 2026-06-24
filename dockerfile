FROM python:3.11-slim

WORKDIR /app

# First install setuptools (fixes pkg_resources error)
RUN pip install --upgrade pip setuptools wheel

# Copy requirements and install
COPY requirements.txt .

# Install with no cache to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]