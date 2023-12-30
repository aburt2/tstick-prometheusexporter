FROM alpine:3.18.4

# Installing required packages
FROM alpine/doctl
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install package
WORKDIR /code
COPY . .
RUN pip3 install .

ENV OSC_PORT="8080"
#has to be EXPORT_PORT 8000 or else it does not work, same applies to the env file
ENV EXPORTER_PORT="8000"
ENV EXPORTER_LOG_LEVEL="INFO"

ENTRYPOINT ["tstick_exporter"]