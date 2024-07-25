FROM tiangolo/uvicorn-gunicorn:python3.11-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./app/config.yaml /opt/config.yaml

COPY ./entrypoint.sh /entrypoint.sh

COPY ./app /app

EXPOSE 8011

ENTRYPOINT ["/entrypoint.sh"]