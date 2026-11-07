FROM python:3.12-slim
WORKDIR /app
COPY groundvalue_mvp/requirements-web.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY groundvalue_mvp /app
RUN useradd --create-home groundvalue && mkdir -p /data && chown -R groundvalue:groundvalue /app /data
USER groundvalue
ENV HOST=0.0.0.0 PORT=8080 GROUNDVALUE_DB=/data/reports.sqlite3
EXPOSE 8080
CMD ["python", "web.py"]
