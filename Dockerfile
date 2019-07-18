FROM python:alpine

RUN pip3 install dramatiq-apscheduler

ENTRYPOINT /usr/local/bin/dramatiq_apscheduler