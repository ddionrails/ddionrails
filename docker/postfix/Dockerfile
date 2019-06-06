FROM python:3.8.0b1-alpine

RUN apk update \
    && apk add postfix \
    && rm -rf /var/cache/apk/*

RUN echo "mynetworks = 172.16.238.10" >> /etc/postfix/main.cf

ENTRYPOINT [ "postfix", "start-fg" ]
