FROM python:3.12-slim
WORKDIR /app
RUN pip install mcp
COPY mcp_servers/customer/server.py .
CMD ["python", "server.py"]
