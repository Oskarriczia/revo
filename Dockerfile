FROM python:3-alpine

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]
#CMD ["uwsgi", "--http", "0.0.0.0:7777", "--master", "--enable-metrics", "--chdir", "src/", "-w", "main:app"]