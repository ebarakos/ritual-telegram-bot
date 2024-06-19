FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR 1
ENV RUNTIME docker
ENV PYTHONPATH src
ARG index_url
ENV UV_EXTRA_INDEX_URL ${index_url}

RUN apt-get update
RUN apt-get install -y git curl

# install uv
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod 755 /install.sh
RUN /install.sh && rm /install.sh

COPY src/requirements.txt .

RUN /root/.cargo/bin/uv pip install --system --no-cache -r requirements.txt

COPY src src

ARG appname
ARG port
ENV APP_NAME=${appname}
ENV PORT=${port}
EXPOSE ${port}
RUN echo '#!/bin/sh\nexec hypercorn "${APP_NAME}:create_app()" -b "0.0.0.0:${PORT}"' > /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]