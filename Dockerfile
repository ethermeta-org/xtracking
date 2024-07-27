FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app/

LABEL org.opencontainers.image.source=https://github.com/ethermeta-org/xtracking

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        libpq-dev \
        libpq5 \
        python3-dev \
        build-essential


# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client-14 \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./app/config.yaml /opt/config.yaml

COPY ./entrypoint.sh /entrypoint.sh

COPY ./app /app/app

RUN mkdir -p /app/data /app/app/data

EXPOSE 8011

ENTRYPOINT ["/entrypoint.sh"]