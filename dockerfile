FROM python:3-slim
COPY requirements.txt /app/requirements.txt
COPY jobs.py /app/jobs.py
RUN pip install --no-cache-dir -r /app/requirements.txt
CMD [ "python", "/app/jobs.py"]