FROM tiangolo/uvicorn-gunicorn:python3.11
COPY src/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY src /app