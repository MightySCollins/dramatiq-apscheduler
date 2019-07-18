FROM python:alpine

RUN apk update && apk add --no-cache tzdata
RUN pip3 install dramatiq-apscheduler

ENV TZ Etc/UTC
ENTRYPOINT ["/usr/local/bin/dramatiq_apscheduler", "tasks.yml"]