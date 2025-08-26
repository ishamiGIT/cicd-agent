FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir ollama

EXPOSE 8082

#CMD ["python", "run.py","--mode","mcp"]
#CMD ["/bin/sh","run.sh"]
CMD ["python","fastmcp_version/run_fastmcp.py", "--mode","mcp"]