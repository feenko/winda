FROM python:3.12.5-slim

RUN mkdir -p /container
WORKDIR /container

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]