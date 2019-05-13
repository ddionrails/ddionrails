FROM python:3.7.3-alpine

RUN apk update \
    && apk add postfix \
    && rm -rf /var/cache/apk/*

RUN echo "mynetworks = 172.16.238.10" >> /etc/postfix/main.cf

ENTRYPOINT [ "postfix", "start-fg" ]
