FROM python:3.12.5-alpine3.20
LABEL maintainer="Patryk Kerlin"

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /tmp/requirements.txt
COPY ./rest_api /rest_api
WORKDIR /rest_api
EXPOSE 8000

RUN python -m venv /pyenv
RUN /pyenv/bin/pip install --upgrade pip
RUN apk add --update --no-cache postgresql-client
RUN /pyenv/bin/pip install -r /tmp/requirements.txt
RUN rm -rf /tmp
RUN adduser -D -H rest-api

ENV PATH="/pyenv/bin:$PATH"

USER rest-api