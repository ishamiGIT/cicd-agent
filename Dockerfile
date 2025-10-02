FROM python:3.10-slim

WORKDIR /app

COPY devops-mcp-server/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY devops-mcp-server .

EXPOSE 9000

ENTRYPOINT ["python", "main.py"]
