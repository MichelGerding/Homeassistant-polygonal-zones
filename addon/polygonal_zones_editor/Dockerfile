ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
    apk update && apk upgrade

RUN \
  apk add --no-cache \
    python3 \
    py3-pip

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install dependencies
RUN \
    pip3 install --upgrade pip && \
    pip3 install starlette uvicorn

WORKDIR /app

COPY app /app
EXPOSE 8000

COPY app/static/zones.json /data/polygonal_zones/zones.json

WORKDIR /app
CMD ["python", "main.py"]
