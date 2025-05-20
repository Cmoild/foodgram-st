FROM python:3.13

WORKDIR /app

RUN pip install gunicorn

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
